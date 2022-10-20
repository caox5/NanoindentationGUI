import os, json
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objs as go
import numpy as np
from threshold import CP


C = ['red', 'blue', 'green', 'pink', 'yellow', 'purple', 'cyan', 'orange', 'brown']

# Pass the build folder's path as the path parameter to declare_component
parent_dir = os.path.dirname(os.path.abspath(__file__))
file_dir = os.path.join(parent_dir, "file_component")
file_component_func = components.declare_component("my_component", path=file_dir)
def file_component(data):
    component_value = file_component_func(data=data, default=0)
    return component_value

# set the page layout
st.set_page_config(layout='wide')
c1, c2, c3 = st.columns([2, 5, 2])

# Initialization
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'datas' not in st.session_state:
    st.session_state.datas = {}

# load the json file
with c1:
    uf = st.file_uploader('Load Json')
    if uf is not None:
        data = json.load(uf)
        cur = []
        ave = []
        curves = data['curves']
        for i in range(len(curves)):
            curve = curves[i]
            z = curve['data']['Z'] = np.array(curve['data']['Z']) * 1e9
            f = curve['data']['F'] = np.array(curve['data']['F']) * 1e9
            if i == 0:
                data.update({'ave': f})
            else:
                zf = np.polyfit(z, f, 3)
                data['ave'] = data['ave'] + np.polyval(zf, curves[0]['data']['Z'])
            cur.append(curve['filename'])
        data['ave'] /= len(curves)
        k = uf.name.split('.')[0]
        st.session_state.datas.update({k: data})
        st.session_state.files.update({k: cur})
    res = file_component(st.session_state.files)
    r = str(res).split(':')
	
with c3:
    CP.yth = st.number_input('Align Threshold [nN]', .0, value=10.)
    CP.dx = st.number_input('Align left step [nm]', .0, 10000., 2000.)
    CP.ddx = st.number_input('AVG area [nm]', .0, value=100.)
    CP.sh = st.number_input('shift CP [nm]', .0)
    force0 = st.checkbox('Set CP force to 0', True)
    if r[0] in st.session_state.datas:
        curve = st.session_state.datas[r[0]]['curves'][int(r[1])]
        st.text(f'Displacemnet SD is {np.std(curve["data"]["Z"])}')
        st.text(f'Force SD is {np.std(curve["data"]["F"])}')
    for k in st.session_state.datas:
        data = st.session_state.datas[k]
        curves = data['curves']
        for curve in curves:
            res = CP.calculate(curve['data']['Z'], curve['data']['F'])
            if res:
                curve.update({'zc': res[0], 'fc': res[1]})
        res = CP.calculate(curves[0]['data']['Z'], data['ave'])
        if res:
            data.update({'zc': res[0], 'fc': res[1]})

with c2:
    datas = []
    for i, k in enumerate(st.session_state.datas):
        data = st.session_state.datas[k]
        curves = data['curves']
        for curve in curves:
            z = curve['data']['Z'] - (curve['zc'] if 'zc' in curve else 0)
            f = curve['data']['F'] - (curve['fc'] if 'fc' in curve and force0 else 0)
            datas.append(go.Scatter(x=z, y=f, opacity=.9, line_color=C[i]))
        z = curves[0]['data']['Z'] - (data['zc'] if 'zc' in data else 0)
        f = data['ave'] - (data['fc'] if 'fc' in data and force0 else 0)
        datas.append(go.Scatter(x=z, y=f, opacity=.9, line={'color': C[i], 'dash': 'dot'}))
    fg = go.Figure(datas)
    fg.update_layout(title='Raw curves', title_x=0.5, title_y=0.99, margin=dict(l=0, r=0, t=30, b=50),
             xaxis_title='Displacement[nm]', yaxis_title='Force[nN]', showlegend=False, height=300,
             legend=dict(x=0.02, y=0.93), xaxis=dict(showgrid=False, zeroline=False),
             yaxis=dict(showgrid=False, zeroline=False))
    st.plotly_chart(fg)

    d = []
    for i, k in enumerate(st.session_state.datas):
        if r[0] != k:
            continue
        curve = st.session_state.datas[r[0]]['curves'][int(r[1])]
        z = curve['data']['Z'] - (curve['zc'] if 'zc' in curve else 0)
        f = curve['data']['F'] - (curve['fc'] if 'fc' in curve and force0 else 0)
        d.append(go.Scatter(x=z, y=f, opacity=.9, line_color=C[i]))
    fl = go.Figure(d)
    fl.update_layout(title='Current curve', title_x=0.5, title_y=0.99, margin=dict(l=0, r=0, t=30, b=50),
             xaxis_title='Displacement[nm]', yaxis_title='Force[nN]', showlegend=False, height=300,
             legend=dict(x=0.02, y=0.93), xaxis=dict(showgrid=False, zeroline=False),
             yaxis=dict(showgrid=False, zeroline=False))
    st.plotly_chart(fl)

