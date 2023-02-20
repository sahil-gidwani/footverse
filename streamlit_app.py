import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Footverse", page_icon="⚽",
                   layout="wide", initial_sidebar_state="auto", menu_items=None)

st.title(f"*Footverse*")
st.markdown("""---""")


@st.cache(allow_output_mutation=True)
def load_standard_data():
    standard_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', 'Matches Played', 'Starts', 'Minutes', '90s', 'Goals', 'Assists', 'Goals + Assists', 'Non-Penalty Goals', 'Penalties Scored',
                   'Penalties Attempted', 'Yellow Cards', 'Red Cards', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'Progressive Carries', 'Progressive Passes', 'Progressive Passes Received', 'Goals p90', 'Assists p90', 'G+A p90', 'npG p90', 'npG+A p90', 'xG p90', 'xAG p90', 'xG+xAG p90', 'npxG p90', 'npxG+xAG p90', '1']
    standard_df.columns = col_headers
    standard_df = standard_df[standard_df['Player'] != 'Player']
    standard_df = standard_df.drop(['0', '1'], axis=1)
    standard_df.reset_index()

    return standard_df


@st.cache(allow_output_mutation=True)
def load_shooting_data():
    shooting_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/shooting/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Goals', 'Shots', 'Shots on Target', 'Shots on Target %',
                   'Shots p90', 'Shots on Target p90', 'Goals per Shot', 'Goals per Shot on Target', 'Shooting Distance', 'Shots from Free Kicks', 'PK', 'PKatt', 'xG', 'npxG', 'npxG per Shot', 'G-xG', 'np:G-xG', '1']
    shooting_df.columns = col_headers
    shooting_df = shooting_df[shooting_df['Player'] != 'Player']
    shooting_df = shooting_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                    'League', 'Age', 'Birth Year', '90s', 'Goals', 'PK', 'PKatt', 'xG', 'npxG'], axis=1)
    shooting_df.reset_index()

    return shooting_df


@st.cache(allow_output_mutation=True)
def load_gsca_data():
    gsca_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/gca/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'SCA', 'SCA p90', 'SCA Pass Live', 'SCA Pass Dead',
                   'SCA Dribbles', 'SCA Shots', 'SCA Fouls Drawn', 'SCA Defensive Actions', 'GCA', 'GCA p90', 'GCA Pass Live', 'GCA Pass Dead', 'GCA Dribbles', 'GCA Shots', 'GCA Fouls Drawn', 'GCA Defensive Actions', '1']
    gsca_df.columns = col_headers
    gsca_df = gsca_df[gsca_df['Player'] != 'Player']
    gsca_df = gsca_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                            'League', 'Age', 'Birth Year', '90s'], axis=1)
    gsca_df.reset_index()

    return gsca_df


@st.cache(allow_output_mutation=True)
def load_possession_data():
    possession_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/possession/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Touches', 'Touches Defensive Penalty', 'Touches Defensive 3rd', 'Touches Middle 3rd',
                   'Touches Attacking 3rd', 'Touches Attacking Penalty', 'Touches Live', 'Dribbles Attempted', 'Dribbles Successful', 'Dribbles Success Rate', 'Dribbles Tackled', 'Dribbles Tackled Rate', 'Carries', 'Carries Total Distance', 'Progressive Carries Distance', 'Progressive Carries', 'Carries Final 3rd', 'Carries Penalty Area', 'Miscontrols', 'Dispossessed', 'Passes Received', 'Progressive Passes Received', '1']
    possession_df.columns = col_headers
    possession_df = possession_df[possession_df['Player'] != 'Player']
    possession_df = possession_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                        'League', 'Age', 'Birth Year', '90s', 'Progressive Carries', 'Progressive Passes Received'], axis=1)
    possession_df.reset_index()

    return possession_df


@st.cache(allow_output_mutation=True)
def load_passing_data():
    passing_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/passing/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Total Passes Completed', 'Total Passes Attempted', 'Total Passes Completion Rate', 'Total Passes Distance', 'Progressive Passes Distance', 'Short Passes Completed', 'Short Passes Attempted', 'Short Passes Completion Rate',
                   'Medium Passes Completed', 'Medium Passes Attempted', 'Medium Passes Completion Rate', 'Long Passes Completed', 'Long Passes Attempted', 'Long Passes Completion Rate', 'Assists', 'xAG', 'xA', 'A-xAG', 'Keypasses', 'Passes Into the Final 3rd', 'Passes Into the 18 Yard Box', 'Crosses Into the 18 Yard Box', 'Progressive Passes', '1']
    passing_df.columns = col_headers
    passing_df = passing_df[passing_df['Player'] != 'Player']
    passing_df = passing_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                  'League', 'Age', 'Birth Year', '90s', 'Assists', 'xAG', 'Progressive Passes'], axis=1)
    passing_df.reset_index()

    return passing_df


@st.cache(allow_output_mutation=True)
def load_passing_types_data():
    passing_types_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/passing_types/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Total Passes Attempted', 'Live Ball Passes', 'Dead Ball Passes', 'Free Kick Passes', 'Passes Back to Defenders', 'Passes Distance>40', 'Crosses', 'Throw Ins', 'Corner Kicks', 'Inswinging Corner Kicks', 'Outswinging Corner Kicks',
                   'Straight Corner Kicks', 'Total Completed Passes', 'Passes Offside', 'Passes Blocked', '1']
    passing_types_df.columns = col_headers
    passing_types_df = passing_types_df[passing_types_df['Player'] != 'Player']
    passing_types_df = passing_types_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                              'League', 'Age', 'Birth Year', '90s', 'Total Passes Attempted', 'Total Completed Passes'], axis=1)
    passing_types_df.reset_index()

    return passing_types_df


@st.cache(allow_output_mutation=True)
def load_defensive_actions_data():
    defensive_actions_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/defense/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Tackles', 'Tackles Won', 'Tackles Defensive 3rd', 'Tackles Middle 3rd', 'Tackles Attacking 3rd', 'Dribblers Tackled',
                   'Dribbled Past + Tackles', 'Tackle %', 'Dribbled Past', 'Blocks', 'Shots Blocked', 'Passes Blocked', 'Interceptions', 'Tackles+Interceptions', 'Clearances', 'Errors Leading to Opponents Shots', '1']
    defensive_actions_df.columns = col_headers
    defensive_actions_df = defensive_actions_df[defensive_actions_df['Player'] != 'Player']
    defensive_actions_df = defensive_actions_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                                      'League', 'Age', 'Birth Year', '90s'], axis=1)
    defensive_actions_df.reset_index()

    return defensive_actions_df


@st.cache(allow_output_mutation=True)
def load_playing_time_data():
    playing_time_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/playingtime/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', 'Matches Played', 'Minutes', 'Minutes per Matches', '% Minutes played', '90s', 'Starts', 'Minutes per Start', 'Completed Matches', 'Subs', 'Minutes per Sub', 'Unused Sub', 'Points per Match',
                   'onG', 'onGA', 'G+/-', 'G+/-90', 'On-Off', 'onxG', 'onxGA', 'xG+/-', 'xG+/-90', 'xOn-Off', '1']
    playing_time_df.columns = col_headers
    playing_time_df = playing_time_df[playing_time_df['Player'] != 'Player']
    playing_time_df = playing_time_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                            'League', 'Age', 'Birth Year', '90s', 'Matches Played', 'Starts', 'Minutes'], axis=1)
    playing_time_df.reset_index()

    return playing_time_df


@st.cache(allow_output_mutation=True)
def load_miscellaneous_data():
    miscellaneous_df = pd.read_html(
        'https://fbref.com/en/comps/Big5/misc/players/Big-5-European-Leagues-Stats')[0]

    col_headers = ['0', 'Player', 'Nation', 'Position', 'Team', 'League', 'Age', 'Birth Year', '90s', 'Yellow Cards', 'Red Cards', 'Second Yellow Cards', 'Fouls Committed', 'Fouls Drawn', 'Offsides', 'Crosses', 'Interceptions', 'Tackles Won', 'Penalties Won', 'Penalties Conceded',
                   'Own Goals', 'Loose Ball Recoveries', 'Aerial Duels Won', 'Aerial Duels Lost', 'Aerial Duels Won %', '1']
    miscellaneous_df.columns = col_headers
    miscellaneous_df = miscellaneous_df[miscellaneous_df['Player'] != 'Player']
    miscellaneous_df = miscellaneous_df.drop(['0', '1', 'Player', 'Nation', 'Position', 'Team',
                                              'League', 'Age', 'Birth Year', '90s', 'Yellow Cards', 'Red Cards', 'Interceptions', 'Tackles Won', 'Crosses'], axis=1)
    miscellaneous_df.reset_index()

    return miscellaneous_df


@st.cache(allow_output_mutation=True)
def merge_data(standard_df, shooting_df, gsca_df, possession_df, passing_df, passing_types_df, defensive_actions_df, playing_time_df, miscellaneous_df):
    merged_df = pd.concat([standard_df, shooting_df, gsca_df, possession_df, passing_df,
                           passing_types_df, defensive_actions_df, playing_time_df, miscellaneous_df], axis=1)

    merged_df['Age'] = merged_df['Age'].astype('string')
    merged_df.dropna(subset=['Age'], inplace=True)
    merged_df['first2'] = merged_df['Age'].str.slice(0, 2)
    merged_df['.'] = '.'
    merged_df['last3'] = merged_df['Age'].str.slice(3, 6)
    merged_df['Age'] = merged_df[[
        'first2', '.', 'last3']].agg(''.join, axis=1)
    merged_df.drop(['first2', '.', 'last3'], axis=1, inplace=True)

    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

    merged_df_columns = list(merged_df.columns)
    del merged_df_columns[0:5]
    merged_df[merged_df_columns] = merged_df[merged_df_columns].apply(
        pd.to_numeric)

    merged_df['League'] = merged_df['League'].replace(
        ['eng Premier League', 'fr Ligue 1', 'de Bundesliga', 'it Serie A', 'es La Liga'], ['Premier League', 'Ligue 1', 'Bundesliga', 'Serie A', 'La Liga'])

    merged_df.reset_index()

    return merged_df


# add specific charts for stats dashboard!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# set precision parameter!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! .style.format(precision=2)
# add a lot of icons

standard_df = load_standard_data()
shooting_df = load_shooting_data()
gsca_df = load_gsca_data()
possession_df = load_possession_data()
passing_df = load_passing_data()
passing_types_df = load_passing_types_data()
defensive_actions_df = load_defensive_actions_data()
playing_time_df = load_playing_time_data()
miscellaneous_df = load_miscellaneous_data()

merged_df = merge_data(standard_df, shooting_df, gsca_df, possession_df, passing_df,
                       passing_types_df, defensive_actions_df, playing_time_df, miscellaneous_df)


def footer():
    st.markdown("""---""")

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # st.write(merged_df)

    st.stop()


nav_option = st.sidebar.radio(
    'Navigation', ('Stats Dashboard', 'Player Comparison', 'Individual Player Scout Report'))


def convert_df_to_csv(df):
    with st.expander("Show Data"):
        st.dataframe(df.style.format(precision=2))
        st.download_button(label="Download data as CSV",
                           data=df.to_csv().encode('utf-8'), mime='text/csv')

    footer()


if (nav_option == 'Stats Dashboard'):
    with st.sidebar:
        st.markdown("""---""")
        st.write('__Filters__')

        leagues_list = list(merged_df['League'].drop_duplicates())
        leagues_list.sort()
        leagues_filter = leagues_list
        if st.checkbox('Choose Leagues:'):
            leagues_filter = st.multiselect(
                '', leagues_list, default=leagues_list)

        filtered_df = merged_df[merged_df['League'].isin(leagues_filter)]
        teams_list = list(filtered_df['Team'].drop_duplicates())
        teams_list.sort()
        teams_filter = teams_list
        if st.checkbox('Choose Teams:'):
            teams_filter = st.multiselect(
                '', teams_list, default=teams_list)
        filtered_df = filtered_df[filtered_df['Team'].isin(teams_filter)]

        gk_list = ['GK']
        df_list = ['DF,FW', 'DF,MF', 'DF']
        mf_list = ['MF,FW', 'MF,DF', 'MF']
        fw_list = ['FW,DF', 'FW,MF', 'FW']
        positions_list = ['GK', 'DF', 'MF', 'FW']
        positions_filter = positions_list
        if st.checkbox('Choose Positions:'):
            positions_filter = st.multiselect(
                '', positions_list, default=positions_list)
        positions_filter_list = []
        if('GK' in positions_filter):
            positions_filter_list += gk_list
        if('DF' in positions_filter):
            positions_filter_list += df_list
        if('MF' in positions_filter):
            positions_filter_list += mf_list
        if('FW' in positions_filter):
            positions_filter_list += fw_list
        filtered_df = filtered_df[filtered_df['Position'].isin(
            positions_filter_list)]

        nations_list = list(filtered_df['Nation'].drop_duplicates())
        nations_list = [str(i) for i in nations_list]
        nations_list.sort()
        nations_filter = nations_list
        if st.checkbox('Choose Nations:'):
            nations_filter = st.multiselect(
                '', nations_list, default=nations_list)
        filtered_df = filtered_df[filtered_df['Nation'].isin(
            nations_filter)]

        age_filter = st.slider('Select a range of Age', 15, 45, (15, 45))
        filtered_df = filtered_df[filtered_df['Age'] >= age_filter[0]]
        filtered_df = filtered_df[filtered_df['Age'] <= age_filter[1]]

    stats_columns = list(merged_df.columns)
    del stats_columns[0:11]  # remove general non-statistical info

    statbox_option = st.selectbox('Choose the Stat:', (stats_columns))

    number_of_players = st.slider(
        'Select number of players whose data you would like to show', 1, 100, 10)

    if('p90' in statbox_option):
        mean_minutes = int(filtered_df['Minutes'].mean())
        minutes_range = st.slider(
            'Minimum minutes played', 0, int(filtered_df['Minutes'].max()), mean_minutes)
        filtered_df = filtered_df[filtered_df['Minutes'] >= minutes_range]

    if(statbox_option == 'Goals + Assists'):
        goals_assists_chart = px.bar(filtered_df.sort_values(
            ['Goals+Assists'], ascending=False).head(number_of_players), x='Player', y=['Goals', 'Assists'],
            hover_data=['Position', 'Team', 'Age', 'Goals+Assists'], color='League', labels={'value': 'Goals + Assists'})
        st.plotly_chart(goals_assists_chart, use_container_width=True)
        goals_assists_df = filtered_df[['Player', 'Nation', 'Position',
                                        'Team', 'League', 'Age', 'Matches Played', 'Goals', 'Assists', 'Goals+Assists']].sort_values(['Goals+Assists'], ascending=False)
        convert_df_to_csv(goals_assists_df)

    if(statbox_option == 'G+A p90'):
        goals_assists_p90_chart = px.scatter(filtered_df.sort_values(
            ['G+A p90'], ascending=False).head(number_of_players), x="Goals p90", y="Assists p90",
            color="League", hover_data=['Player', 'Position', 'Team', 'Age'], size='G+A p90')
        st.plotly_chart(goals_assists_p90_chart, use_container_width=True)
        goals_assists_p90_df = filtered_df[['Player', 'Nation', 'Position',
                                            'Team', 'League', 'Age', 'Matches Played', 'Goals p90', 'Assists p90', 'G+A p90']].sort_values(['G+A p90'], ascending=False)
        convert_df_to_csv(goals_assists_p90_df)

    if(statbox_option == 'xG+xA p90'):
        x_goals_assists_p90_chart = px.scatter(filtered_df.sort_values(
            ['xG+xA p90'], ascending=False).head(number_of_players), x="xG p90", y="xA p90",
            color="League", hover_data=['Player', 'Position', 'Team', 'Age'], size='xG+xA p90')
        st.plotly_chart(x_goals_assists_p90_chart, use_container_width=True)
        x_goals_assists_p90_df = filtered_df[['Player', 'Nation', 'Position',
                                              'Team', 'League', 'Age', 'Matches Played', 'xG p90', 'xA p90', 'xG+xA p90']].sort_values(['xG+xA p90'], ascending=False)
        convert_df_to_csv(x_goals_assists_p90_df)

    stat_chart = px.bar(filtered_df.sort_values(
        [statbox_option], ascending=False).head(number_of_players), x='Player', y=statbox_option,
        hover_data=['Position', 'Team', 'Age'], color='League')
    st.plotly_chart(stat_chart, use_container_width=True)

    stat_df = filtered_df[['Player', 'Nation', 'Position',
                           'Team', 'League', 'Age', 'Matches Played', statbox_option]].sort_values([statbox_option], ascending=False)
    convert_df_to_csv(stat_df)


def plot_radar_chart(i1, i2):
    stats_player1 = player1_df.iloc[:, i1:i2]
    stats_player2 = player2_df.iloc[:, i1:i2]
    stats_categories = list(stats_player1.columns)

    def conditional_formatting_rows(row):
        highlight_green = 'color: lawngreen;'
        highlight_red = 'color:red'
        default = ''
        if row[player_choice1] > row[player_choice2]:
            return [highlight_green, highlight_red]
        elif row[player_choice2] > row[player_choice1]:
            return [highlight_red, highlight_green]
        else:
            return [default, default]

    player_comparison_df = pd.concat(
        [stats_player1, stats_player2], axis=0).reset_index()

    player_comparison_df.drop(columns=['index'], inplace=True)
    player_comparison_df = player_comparison_df.T
    player_comparison_df.columns = [player_choice1, player_choice2]

    st.dataframe(player_comparison_df.style.apply(conditional_formatting_rows, subset=[
        player_choice1, player_choice2], axis=1).format(precision=2))
    st.download_button(label="Download data as CSV",
                       data=player_comparison_df.to_csv().encode('utf-8'), mime='text/csv')

    st.markdown("""---""")

    if (st.checkbox('Choose stats:')):
        stats_categories = st.multiselect(
            '', list(stats_player1.columns), default=list(stats_player1.columns))

    radar_chart = go.Figure()
    radar_chart.add_trace(go.Scatterpolar(
        r=stats_player1[stats_categories].values.flatten().tolist(), theta=stats_categories, fill='toself', name=player_choice1))
    radar_chart.add_trace(go.Scatterpolar(
        r=stats_player2[stats_categories].values.flatten().tolist(), theta=stats_categories, fill='toself', name=player_choice2))
    radar_chart.update_layout(polar=dict(bgcolor='#1e2130',
                                         radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(radar_chart, use_container_width=True)

    footer()


if (nav_option == 'Player Comparison'):
    # normalize data !!!!!!!!!!!!!!!!!!!!!!!!!
    lc, rc = st.columns(2)

    with lc:
        leagues1 = list(merged_df['League'].drop_duplicates())
        leagues1.sort()
        league_choice1 = st.radio(
            'Select League:', leagues1, key=1)
        league_df1 = merged_df[merged_df['League'] == league_choice1]

        teams1 = list(league_df1['Team'].drop_duplicates())
        teams1.sort()
        team_choice1 = st.selectbox('Select Team:', teams1, key=11)
        teams_df1 = league_df1[league_df1['Team'] == team_choice1]

        gk_list = ['GK']
        df_list = ['DF,FW', 'DF,MF', 'DF']
        mf_list = ['MF,FW', 'MF,DF', 'MF']
        fw_list = ['FW,DF', 'FW,MF', 'FW']
        positions_list = ['GK', 'DF', 'MF', 'FW']
        positions_filter = positions_list
        positions_filter = st.selectbox(
            'Select Position:', positions_list, key=111)
        positions_filter_list = []
        if('GK' in positions_filter):
            positions_filter_list += gk_list
        if('DF' in positions_filter):
            positions_filter_list += df_list
        if('MF' in positions_filter):
            positions_filter_list += mf_list
        if('FW' in positions_filter):
            positions_filter_list += fw_list
        positions_df1 = teams_df1[teams_df1['Position'].isin(
            positions_filter_list)]

        players1 = list(positions_df1['Player'])
        players1.sort()
        player_choice1 = st.selectbox('Select Player:', players1, key=1111)
        player1_df = positions_df1[positions_df1['Player']
                                   == player_choice1].reset_index()

    with rc:
        leagues2 = list(merged_df['League'].drop_duplicates())
        leagues2.sort()
        league_choice2 = st.radio(
            'Select League:', leagues2)
        league_df2 = merged_df[merged_df['League'] == league_choice2]

        teams2 = list(league_df2['Team'].drop_duplicates())
        teams2.sort()
        team_choice2 = st.selectbox('Select Team:', teams2)
        teams_df2 = league_df2[league_df2['Team'] == team_choice2]

        gk_list = ['GK']
        df_list = ['DF,FW', 'DF,MF', 'DF']
        mf_list = ['MF,FW', 'MF,DF', 'MF']
        fw_list = ['FW,DF', 'FW,MF', 'FW']
        positions_list = ['GK', 'DF', 'MF', 'FW']
        positions_filter = positions_list
        positions_filter = st.selectbox(
            'Select Position:', positions_list)
        positions_filter_list = []
        if('GK' in positions_filter):
            positions_filter_list += gk_list
        if('DF' in positions_filter):
            positions_filter_list += df_list
        if('MF' in positions_filter):
            positions_filter_list += mf_list
        if('FW' in positions_filter):
            positions_filter_list += fw_list
        positions_df2 = teams_df2[teams_df2['Position'].isin(
            positions_filter_list)]

        players2 = list(positions_df2['Player'])
        if(player_choice1 in players2):
            players2.remove(player_choice1)
        players2.sort()
        player_choice2 = st.selectbox('Select Player:', players2)
        player2_df = positions_df2[positions_df2['Player']
                                   == player_choice2].reset_index()

    st.markdown("""---""")

    categories = ['Standard', 'Shooting',
                  'Goal and Shot Creation', 'Possession', 'Passing', 'Pass Types', 'Defensive Actions', 'Playing Time', 'Miscellaneous']
    category_choice = st.selectbox('', categories)

    st.markdown("""---""")

    if(category_choice == 'Standard'):
        plot_radar_chart(8, 37)

    if(category_choice == 'Shooting'):
        plot_radar_chart(37, 49)

    if(category_choice == 'Goal and Shot Creation'):
        plot_radar_chart(49, 65)

    if(category_choice == 'Possession'):
        plot_radar_chart(65, 85)

    if(category_choice == 'Passing'):
        plot_radar_chart(85, 105)

    if(category_choice == 'Pass Types'):
        plot_radar_chart(105, 118)

    if(category_choice == 'Defensive Actions'):
        plot_radar_chart(118, 133)

    if(category_choice == 'Playing Time'):
        plot_radar_chart(133, 151)

    if(category_choice == 'Miscellaneous'):
        plot_radar_chart(151, 162)

if(nav_option == 'Individual Player Scout Report'):
    gk_list = ['GK']
    df_list = ['DF,FW', 'DF,MF', 'DF']
    mf_list = ['MF,FW', 'MF,DF', 'MF']
    fw_list = ['FW,DF', 'FW,MF', 'FW']

    @st.cache
    def gk_percentile_rank():
        positions_df = merged_df[merged_df['Position'].isin(gk_list)]
        gk_percentile_df = positions_df
        for each in positions_df.columns:
            gk_percentile_df[f'{each} percentile rank'] = positions_df[each].rank(
                pct=True)
        return gk_percentile_df

    @st.cache
    def df_percentile_rank():
        positions_df = merged_df[merged_df['Position'].isin(df_list)]
        df_percentile_df = positions_df
        for each in positions_df.columns:
            df_percentile_df[f'{each} percentile rank'] = positions_df[each].rank(
                pct=True)
        return df_percentile_df

    @st.cache
    def mf_percentile_rank():
        positions_df = merged_df[merged_df['Position'].isin(mf_list)]
        mf_percentile_df = positions_df
        for each in positions_df.columns:
            mf_percentile_df[f'{each} percentile rank'] = positions_df[each].rank(
                pct=True)
        return mf_percentile_df

    @st.cache
    def fw_percentile_rank():
        positions_df = merged_df[merged_df['Position'].isin(fw_list)]
        fw_percentile_df = positions_df
        for each in positions_df.columns:
            fw_percentile_df[f'{each} percentile rank'] = positions_df[each].rank(
                pct=True)
        return fw_percentile_df

    leagues = list(merged_df['League'].drop_duplicates())
    leagues.sort()
    league_choice = st.radio(
        'Select League:', leagues)
    filtered_df = merged_df[merged_df['League'] == league_choice]

    teams = list(filtered_df['Team'].drop_duplicates())
    teams.sort()
    team_choice = st.selectbox('Select Team:', teams)
    filtered_df = filtered_df[filtered_df['Team'] == team_choice]

    positions_list = ['GK', 'DF', 'MF', 'FW']
    positions_filter = positions_list
    positions_filter = st.selectbox(
        'Select Position:', positions_list)
    positions_filter_list = []
    if('GK' in positions_filter):
        positions_filter_list += gk_list
    if('DF' in positions_filter):
        positions_filter_list += df_list
    if('MF' in positions_filter):
        positions_filter_list += mf_list
    if('FW' in positions_filter):
        positions_filter_list += fw_list
    filtered_df = filtered_df[filtered_df['Position'].isin(
        positions_filter_list)]

    players = list(filtered_df['Player'])
    players.sort()
    player_choice = st.selectbox('Select Player:', players)

    if(positions_filter == 'GK'):
        percentile_df = gk_percentile_rank()
    if(positions_filter == 'DF'):
        percentile_df = df_percentile_rank()
    if(positions_filter == 'MF'):
        percentile_df = mf_percentile_rank()
    if(positions_filter == 'FW'):
        percentile_df = fw_percentile_rank()

    player_df = percentile_df[percentile_df['Team'] == team_choice]
    player_df = player_df[player_df['Player']
                          == player_choice].reset_index()

    stats = list(player_df.columns)
    percentile_rank = stats[169:323]
    stats = stats[8:162]
    stats_value = player_df.iloc[:, 8:162].values.flatten().tolist()
    percentile_rank_values = player_df.iloc[:,
                                            169:323].values.flatten().tolist()

    scout_report_df = pd.DataFrame(
        {'Statistics': stats, 'Value': stats_value, 'Percentile': percentile_rank_values})
    scout_report_df = scout_report_df.set_index('Statistics')
    st.write(scout_report_df)

    with st.expander('Standard', expanded=True):
        st.dataframe(scout_report_df.iloc[0:29, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Shooting'):
        st.dataframe(scout_report_df.iloc[29:41, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Goal and Shot Creation'):
        st.dataframe(scout_report_df.iloc[41:57, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Possession'):
        st.dataframe(scout_report_df.iloc[57:77, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Passing'):
        st.dataframe(scout_report_df.iloc[77:97, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Pass Types'):
        st.dataframe(scout_report_df.iloc[97:110, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Defensive Actions'):
        st.dataframe(scout_report_df.iloc[110:125, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Playing Time'):
        st.dataframe(scout_report_df.iloc[125:143, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    with st.expander('Miscellaneous'):
        st.dataframe(scout_report_df.iloc[143:154, :].style.format({'Percentile': "{:.2%}"}).background_gradient(
            cmap='RdYlGn', subset=['Percentile']).format(precision=2, subset=['Value']))

    st.download_button(label="Download data as CSV",
                       data=scout_report_df.to_csv().encode('utf-8'), mime='text/csv')

    footer()
