# ai-trust-testbed

## Running the Software

Running the testbed should be as simple as `python3 main.py` from within `ai-trust-testbed`.  There are a few dependencies that may have to be addressed, however.  You must have `python3` and `pip3` on your system, in addition to a few python packages listed below.  They can be installed using `pip3 install [packagename]`.  If you wish to install the packages locally, this can be done by adding the `--user` flag.

* `scipy`
* `numpy`
* `sklearn`
* `joblib`
* `pyyaml`

### `ai/`
A program designed for a study involving participants' trust in an artificial intelligence.  This is tested by asking the participant to "bet" on horse races where an AI has predicted the outcome.  Researchers will then observe the participant's actions while choosing their bet, as an indication of trust, (i.e. choosing the AI's suggestion, amount of time taken, etc).

Data used for the AI will be located in `data/`, which is a symlink to the shared directory `/opt/summer17/data`.
This will contain data from the formulator website, as it was downloaded.  A user can run `compile_data.py` (after configuring the compilation in `config.py`), which scrapes the data found in the linked directory to generate a single (large) data file for use for a given AI, depending on the settings found in the config file.  This file can be found at `data.csv` by default.

Once the data has been compiled into `data.csv` and `LABELS.data.csv`, then `learn.py` can be run to, using SciKit Learn, fit to the data and predict either finishing time or Beyer Speed Figures of horses.  Using `learn.py`, we have researched the best prediction model for our data, and those models have been saved in pickle objects as `ai_{time,beyer}.py`.  These models are then used by the `lib/load_ai.py` connector to gather a list of horses and predicted figures for the testbed.

### `ui/`

The majority of the testbed is run from `ui/Graphics.py`, which creates the screens available.  There is a settings screen for the researcher, to adjust various parameters (such as the amount of information from the AI to be shown), as well as an instructions screen for the participant, as a short tutorial on the workings of the GUI.  The participant is then taken to the betting screen, where they are shown information on a horse race and three of the horses racing, and must choose which horse is the likely winner.  The user is also shown a prediction by our AI.  After a few trials, the participant fetches their researcher, who then saves the data to file.
