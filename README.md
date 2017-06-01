# ai-trust-testbed
A program designed for a study involving participants' trust in an artificial intelligence.  This is tested by asking the participant to "bet" on horse races where an AI has predicted the outcome.  Researchers will then observe the participant's actions while choosing their bet, as an indication of trust, (i.e. choosing the AI's suggestion, amount of time taken, etc).

Data used for the AI will be located in `../data`, which allows read access to everyone (`774`).  On gemini, this directory is `~amcarthu/summer-research-2017/data`.
This will contain data from the formulator website, as it was downloaded.  A user can run `compile_data.py` (after configuring the compilation in `config.py`), which scrapes the data found in `../data` to generate a single (large) data file for use for a given AI, depending on the settings found in the config file.  This file can be found at `data.csv` by default.

This data will be compiled for one of three problems, each to by solved by their own AI (and therefore requiring different forms of the data).  In the config file, these problems are referred to as `PREDICT_TIME_AI`, `PREDICT_BSF_AI`, and `PREDICT_WINNER_AI`.  

- `PREDICT_TIME_AI` (1): 
    - Input: Information on a horse for a specific race, as well as the race conditions
    - Output: The horse's finishing time for that race

- `PREDICT_BSF_AI` (2): 
    - Input: Information on a horse for a specific race, as well as the race conditions
    - Output: The horse's Beyer Speed Figure for that race

- `PREDICT_WINNER_AI` (3): 
    - Input: information on two horses for a specific race, as well as the race conditions
    - Output: Indication which horse wins the race
