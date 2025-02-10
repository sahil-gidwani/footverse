import streamlit as st

st.set_page_config(page_title="Stats Dashboard", page_icon="📊", layout="wide")

st.title("📊 Stats Dashboard")
st.caption("Explore Football Data with Interactive Visualizations! 📈")
st.markdown("---")

if 'outfield_df' not in st.session_state:
    from data.data_loader import store_session_data
    store_session_data()

outfield_df = st.session_state.outfield_data

with st.sidebar:
	st.write('__Filters__')
	
	# Sidebar - Team selection
	leagues_list = list(outfield_df['League'].drop_duplicates())
	leagues_list.sort()
	leagues_filter = leagues_list
	if st.checkbox('Choose Leagues:'):
		leagues_filter = st.multiselect(
			'', leagues_list, default=leagues_list)

	filtered_df = outfield_df[outfield_df['League'].isin(leagues_filter)]
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

	nations_list = list(filtered_df['Nationality'].drop_duplicates())
	nations_list = [str(i) for i in nations_list]
	nations_list.sort()
	nations_filter = nations_list
	if st.checkbox('Choose Nations:'):
		nations_filter = st.multiselect(
			'', nations_list, default=nations_list)
	filtered_df = filtered_df[filtered_df['Nationality'].isin(
		nations_filter)]

	age_filter = st.slider('Select a range of Age', 15, 45, (15, 45))
	filtered_df = filtered_df[filtered_df['Age'] >= age_filter[0]]
	filtered_df = filtered_df[filtered_df['Age'] <= age_filter[1]]
