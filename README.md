# Serif Health Takehome Interview - Solution

This distrubution assumes you are running on \*nix OS (including MacOS)

### Pre-Requisites

1. An internet connection.
1. You should have `python3` installed (should already be installed on more recent \*nix systems)
1. You need to download the Anthem index file from [here](https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/2023-04-01_anthem_index.json.gz)
1. Unzip this file, then set `INDEX_FILEPATH` in `config.py` to the filepath of this file.
1. Set the value for `OUTPUT_FILEPATH` in `config.py` this is the location of the csv file that will be produced by running this script

### Install Dependencies and Run Solution code:

Open terminal, `cd` into this directory and run `$ source run.sh` to install dependencies and run the solution code (Note to run the solution code more than once, just run this script again, the dependencies will be recognised as satisfied).

### Goal

Answer this question: What is the list of file URLs that represent the Anthem PPO network in New York state?

### Background on Approach used

There appears to be two available sources to obtain URLs for the in-network files for Anthem PPO NY:

1. The nested structures in the json index file: `reporting_structure[array] > item[obj] > in_network_files[array] > item[obj] > location[string]`
2. The provided resource to find in network files as an EIN look up online: [here](https://www.anthem.com/machine-readable-file/search/)

While a more complete solution may look to obtain data from both of these sources. I have chosen to concentrate on the latter as it seems like the hint is pushing me in that direction. The final solution willl therefore follow these steps:

1. Find the API link used by the service in option 2 so that I can codify the process of getting a list of "In-Network Negotiated Rates File" urls from an EIN
1. Extract all Plan EINs from the index file where the plan name includes `PPO` and `NY`
1. Pull all urls from the EIN look up API that contain `PPO` and `NY` in the filenames
1. Write results to a csv file

This solution avoids having to traverse all of the confusing filepaths that are written in the index file.

I have included the final solution file `anthem_ny_ppo_urls.csv`. I would not normally add data to a repo but since this is part of the final solution and the file is not too big I thought it made sense to include it.

### Assumptions, Constraints, and what I would do with more time

Given more time I would look to ensure this solution is accurate and potentially uses the filepaths from the index file if needed. Moreover, I have also assumed that all PPO NY Plans would contain `PPO` and `NY` in the name. This is another major assumption.

However, I believe the assumption that the `displayname` for each url from the EIN lookup portal containing `PPO` and `NY` for all `PPO NY` files is reasonable.

I chose to store the urls in memory in a `python set` to make de-duping computationally cheap. While this was achieved I think I would have preferred to simply use a `python dict` and set the keys to be the `displayname` from the API. While I belive both these data structures use hash tables under the hood, I think the latter solution may have provided a more expressive output since the URLs are not as expressive as this display name.

### Observations from executing solution

- The time it took to complete the job was ~ 30 minutes on my system. Mostly because there were not too many Plans that had an EIN available and had `NY` and `PPO` in the name.
- If looking to reduce time/ increase speed to complete I could leverage the python `multiprocessing` module to chunk up the EINs and map reduce the job just on my local system.
- A Simple way to use less memory would be to write the results to disk and de-dup afterwards. This would take more time, use more disk space and less RAM. However the memory usage on my laptop during run time seemed negligible. This would be useful If I wanted to check all EINs contained in the index file.
