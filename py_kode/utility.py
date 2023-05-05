def get_fpl_data():
    return requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()

def get_element_data(fpl_data):
    return pd.DataFrame(fpl_data['elements'])

def get_team_data(fpl_data):
    return pd.DataFrame(fpl_data['teams'])

def generate_team_elements(element_data, team_data):
    return pd.merge(element_data, team_data,
                             left_on='team', right_on='id')

def generate_review_data():
    review_data = pd.read_csv("Data/fplreview.csv")
    review_data = review_data.fillna(0)
    review_data['review_id'] = review_data.index+1
    return review_data

def generate_merged_data(elements_team, review_data):
    merged_data = pd.merge(elements_team, review_data,
                           left_on='id_x', right_on='review_id')
    merged_data.set_index(['id_x'], inplace=True)

    return merged_data

def generate_type_data(fpl_data):
    return pd.DataFrame(fpl_data['element_types']).set_index(['id'])

def return_noised_merged_data(merged_data, gw, horizon):
    rng = np.random.default_rng(seed=seed_val)
    gws = list(range(gw+1, min(39, gw+1+horizon)))
    for w in gws:
        noise = merged_data[f"{w}_Pts"] * (
            92 - merged_data[f"{w}_xMins"]) / 134 * rng.standard_normal(size=len(merged_data))
        merged_data[f"{w}_Pts"] = merged_data[f"{w}_Pts"] + noise
    
    return merged_data

def get_merged_data(elements_team, review_data, randomized, gw, horizon):
    merged_data = generate_merged_data(elements_team, review_data)

    if randomized:
        merged_data = return_noised_merged_data(merged_data, gw, horizon)
    
    return merged_data

def fetch_picks_data(team_id, gw):
    return requests.get(f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/').json()

def get_initial_squad(team_id, gw):
    picks_data = fetch_picks_data(team_id, gw)
    return [i['element'] for i in picks_data['picks']]

def get_itb(team_id):
    return requests.get(f'https://fantasy.premierleague.com/api/entry/{team_id}/').json()['last_deadline_bank'] / 10
