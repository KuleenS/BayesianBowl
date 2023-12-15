import logging

from logging.handlers import QueueHandler

from multiprocessing import Queue, Process, current_process, cpu_count

import os

import pickle

import re

import requests

import sys

import time

import traceback

from typing import List, Tuple

from unicodedata import normalize

from bs4 import BeautifulSoup

import numpy as np

from tqdm import tqdm


# holding class for individuals who play in tourmanet

class Individual:
    def __init__(
        self,
        team: str,
        id: int,
        header: List[str],
        scores: List[Tuple[List[str], List[str]]],
    ):
        self.team = team
        self.id = id
        self.header = header
        self.scores = scores


# holding class for all data related to tourmanent

class Tournament:
    def __init__(
        self,
        tourn_id: int,
        packets: str,
        headers: List[List[str]],
        round_scores: List[Tuple[List[str], List[str]]],
        individuals: List[Individual],
    ):
        self.id = tourn_id
        self.packets = packets
        self.headers = headers
        self.round_scores = round_scores
        self.individuals = individuals


# function to extract all the individuals and their scores from the tournament they played at
def extract_individuals(tournament):

    # get tourmanet website
    data = BeautifulSoup(
        requests.get(
            f"https://www.naqt.com"
            + tournament.replace("standings", "individuals")
            + "&playoffs=true"
        ).text,
        features="html.parser",
    )

    if (
        len(
            data.findAll(
                string="No individual statistics are currently available for this tournament."
            )
        )
        != 0
    ):
        return []

    individuals = [
        x.find("a").get("href") for x in data.find_all("th", attrs={"data-order": True})
    ]

    # loop through all indivduals and get their scores
    individual_classes = []

    for individual in individuals:
        individual_webpage = BeautifulSoup(
            requests.get(f"https://www.naqt.com" + individuals[0]).text,
            features="html.parser",
        )

        # get the team they play for
        team = individual_webpage.find(
            "a", href=re.compile("/stats/school/results.jsp")
        ).text

        # get the column header for their stats so we know which stats were recorded
        header = [x.text for x in individual_webpage.find("thead").find_all("th")]

        # get their unique id
        individual_id = individual_webpage.find(
            "a", href=re.compile("/stats/player/index.jsp")
        )

        if individual_id is None:
            individual_id = individual_webpage.find("h2").text
        else:
            individual_id = (
                individual_id.get("href").split("?")[-1].replace("contact_id=", "")
            )

        # get their scores from the webpage
        scores = [
            ([x.text for x in x.find_all("a")], [x.text for x in x.find_all("td")])
            for x in individual_webpage.find_all("tr", attrs={"class": "game"})
        ]

        individual_class = Individual(team, individual_id, header, scores)

        individual_classes.append(individual_class)

    return individual_classes


# function to extract scores from tournament
def extract_scores(tournament):
    i = 1

    headers = []

    rounds_scores = []

    packets = []

    # loops through all the rounds of a tournament
    while True:
        # get the round
        data = BeautifulSoup(
            requests.get(
                "https://www.naqt.com"
                + tournament.replace("standings", "round")
                + f"&round={i}"
            ).text,
            features="html.parser",
        )

        # break if no scores
        if len(data.findAll(string="There are no games in this round.")) != 0:
            break

        header = data.find("thead")

        # get column header to see what stats were recorded
        header_data = [x.text for x in header.find_all("th")]

        # get scores
        round_scores = [
            ([x.text for x in x.find_all("a")], [x.text for x in x.find_all("td")])
            for x in data.find_all("tr", attrs={"class": "prelim"})
        ]

        # get which packet they were playing on 
        packet = [
            x
            for x in data.find("section", attrs={"id": "tournament-info"}).find_all(
                "tr"
            )
            if x.text.find("Questions") != -1
        ]

        # clean up packet data
        if len(packet) == 0:
            packet = data.find("h1").text
        else:
            packet = packet[0].find("th").text
        packet = normalize("NFKD", packet)

        headers.append(header_data)
        rounds_scores.append(round_scores)
        packets.append([packet] * len(header_data))

        i += 1

    return headers, rounds_scores, packets


# helper function to set up shared queue for logging to one output
def worker_configurer(queue):
    h = QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    # send all messages, for demo; no other level or filter logic applied.
    root.setLevel(logging.INFO)


# function of work for one process to scrape an area
def worker_process(queue, work_queue, configurer):
    # confuiger worker with logging
    configurer(queue)

    name = current_process().name
    logger = logging.getLogger()
    logger.info("Worker started: %s" % name)
    
    # work while there is work in queue
    while work_queue.qsize() > 0:
        tournament = work_queue.get()

        logger.info(f"Starting scraping {tournament}")

        logger.info(f"Queue is now {work_queue.qsize()}")

        try:
            # extract scores from tourmanets
            headers, rounds_scores, packets = extract_scores(tournament)

            # extract individual performances
            individuals = extract_individuals(tournament)

            # clean up torumanet id
            tournament_id = tournament.split("?")[-1].replace("tournament_id=", "")

            tournament_class = Tournament(
                tournament_id, packets, headers, rounds_scores, individuals
            )

            # save tourmanet data
            with open(f"raw_data/tournament_{tournament_id}.pickle", "wb") as f:
                pickle.dump(tournament_class, f)

            logger.info(f"Ending scraping {tournament}")

        except:
            logger.info(f"{tournament} failed")
            time.sleep(60)

    logger.info("Worker finished: %s" % name)


# set up process that aggregates all the logs and prints them to standard out
def listener_configurer():
    root = logging.getLogger()
    h = logging.StreamHandler()
    f = logging.Formatter(
        "%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s"
    )
    h.setFormatter(f)
    root.addHandler(h)


# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            # constantly wait for new messages
            record = queue.get()
            if (
                record is None
            ):  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            logger.error("Whoops! Problem:", file=sys.stderr)
            logger.error(e, file=sys.stderr)


def main():

    # get all tournaments recorded by NAQT
    total_tournaments = []

    for i in tqdm(range(1996, 2024)):
        data = BeautifulSoup(
            requests.get(f"https://www.naqt.com/stats/tournament/?year_code={i}").text,
            features="html.parser",
        )

        # get the link to the stats
        tournament_stats = [
            x.get("href")
            for x in data.find("section", attrs={"id": "results"}).find_all("a")
            if x.get("href").find("stats") != -1
        ]

        total_tournaments.extend(tournament_stats)

    gotten_files = [
        x.split("_")[-1].replace(".pickle", "") for x in os.listdir("raw_data/")
    ]

    print(len(total_tournaments))
    
    # filter all tournaments that we have done already
    total_tournaments = [
        x
        for x in total_tournaments
        if x.split("=")[-1] not in gotten_files and "standings.jsp?tournament_id=" in x
    ]

    print(len(total_tournaments))

    # use two processes to get twice the speed
    num_workers = 2

    queue = Queue(-1)
    work_queue = Queue(-1)
    
    # start the printing process
    listener = Process(target=listener_process, args=(queue, listener_configurer))
    listener.start()

    # put all the tournaments in a shared queue so that the processes can constantly get more websites to scrape
    for tournament in total_tournaments:
        work_queue.put(tournament)

    workers = []
    
    # dispatch workers
    for i in range(num_workers):
        worker = Process(
            target=worker_process, args=(queue, work_queue, worker_configurer)
        )
        workers.append(worker)
        worker.start()

    for w in workers:
        w.join()

    queue.put_nowait(None)
    listener.join()


if __name__ == "__main__":
    main()
