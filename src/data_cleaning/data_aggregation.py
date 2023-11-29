import os

import pickle 

import pandas as pd

from src.object.individual import Individual
from src.object.tournament import Tournament

total_headers = ['Winner_Ltng',
'Loser_Ltng',
 'Loser',
 'Winner',


 'Winner_Score',
 'Loser_Score',

 'Winner_BB%',
 'Loser_BB%',

 'Winner_TU',
 'Loser_TU',

 'Winner_BO',
 'Loser_BO',

 'Winner_Wksht',
 'Loser_Wksht',

 'Result',

 'Winner_P',
 'Loser_P',

 'Winner_BB',
 'Loser_BB',

 'Winner_I',
 'Loser_I',

 'Winner_PPB',
 'Loser_PPB',

 'Winner_Ltng/Wksht',
 'Ltng/Wksht',

 'Team',
 
 'Winner_B',
 'Loser_B',

 'Player'

 'TUH',
]

path = "../../data/"
tournaments  = [os.path.join(path, x) for x in os.listdir(path)]

rounds_data = []

for pickle_ in tqdm(tournaments):
    with open(pickle_, "rb") as f:
        try:
            data = pickle.load(f)
        except EOFError:
            print(pickle_)
        if len(data.headers) != 0 and len(data.round_scores) != 0 and len(data.round_scores[0]) != 0:
            for headers, round_ in zip(data.headers, data.round_scores):
                indices_winner = headers.index("Winner")
                indices_loser = headers.index("Loser")

                for match in round_:

                    round_data = dict.fromkeys(total_headers)

                    match[1].insert(indices_winner, match[0][0])
                    match[1].insert(indices_loser, match[0][1])

                    for i, (key, value) in enumerate(zip(headers, match[1])):

                        if key not in ["Winner", "Loser", "TUH", "Team", "Player", "Result"]:

                            if i < indices_loser:
                                round_data["Winner_" + key] = value
                            
                            elif i > indices_loser:
                                round_data["Loser_" + key] = value
                        
                        else:
                            round_data[key] = value
                    
                    rounds_data.append(round_data)

pd.DataFrame(rounds_data).to_csv("dataset.csv", index=False)