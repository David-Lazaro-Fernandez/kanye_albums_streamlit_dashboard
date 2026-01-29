import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Kanye West - Discografía Dashboard",
    page_icon="🎵",
    layout="wide"
)

# URLs de los covers de los álbumes
COVERS = {
    "The College Dropout": "https://upload.wikimedia.org/wikipedia/en/a/a3/Kanyewest_collegedropout.jpg",
    "Late Registration": "https://upload.wikimedia.org/wikipedia/en/f/f4/Late_registration_cd_cover.jpg",
    "Graduation": "https://upload.wikimedia.org/wikipedia/en/7/70/Graduation_%28album%29.jpg",
    "808s & Heartbreak": "https://upload.wikimedia.org/wikipedia/en/f/f1/808s_%26_Heartbreak.png",
    "My Beautiful Dark Twisted Fantasy": "https://upload.wikimedia.org/wikipedia/en/thumb/b/be/MBDTF_ALT.jpg/250px-MBDTF_ALT.jpg",
    "Yeezus": "https://upload.wikimedia.org/wikipedia/en/0/03/Yeezus_album_cover.png",
    "The Life Of Pablo": "https://upload.wikimedia.org/wikipedia/en/4/4d/The_life_of_pablo_alternate.jpg",
    "ye": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSlZISgvD0UqauOZPmCFmhXbMhO9nMsLT1ZqQ&s",
    "Jesus Is King": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRc9azuiXWdA1MChodyAylTV8b4jJ3MikrWBA&s",
    "Donda": "https://upload.wikimedia.org/wikipedia/commons/6/60/Kanye_donda.jpg",
    "VULTURES 1": "https://static.wikia.nocookie.net/kanyewest/images/7/7b/Vulturessingle.png/revision/latest/thumbnail/width/360/height/450?cb=20231221203318",
    "VULTURES 2": "https://upload.wikimedia.org/wikipedia/en/6/66/%C2%A5%24_-_Vultures_2.png",
    "MERCY (Single)": "https://upload.wikimedia.org/wikipedia/en/a/a3/Kanyewest_collegedropout.jpg",
}

# Función para formatear números grandes
def format_plays(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    return str(num)

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("albums.csv")
    df['plays'] = pd.to_numeric(df['plays'], errors='coerce')
    return df

df = load_data()

# Título principal
st.title("🎤 Kanye West - Dashboard de Discografía")
st.markdown("---")

# ============= MÉTRICAS PRINCIPALES =============
st.header("📊 Estadísticas Generales")

col1, col2, col3, col4 = st.columns(4)

# Canción más escuchada
top_song = df.loc[df['plays'].idxmax()]

# Álbum con más reproducciones
album_plays = df.groupby('album')['plays'].sum().reset_index()
top_album = album_plays.loc[album_plays['plays'].idxmax()]

# Total de reproducciones
total_plays = df['plays'].sum()

# Total de canciones
total_songs = len(df)

with col1:
    st.metric("🎵 Total de Canciones", total_songs)

with col2:
    st.metric("▶️ Reproducciones Totales", format_plays(total_plays))

with col3:
    st.metric("🏆 Canción Más Escuchada", top_song['track'])
    st.caption(f"Del álbum: {top_song['album']}")
    st.caption(f"Reproducciones: {format_plays(top_song['plays'])}")

with col4:
    st.metric("💿 Álbum Más Escuchado", top_album['album'])
    st.caption(f"Reproducciones: {format_plays(top_album['plays'])}")

st.markdown("---")

# ============= TOP 10 CANCIONES =============
st.header("🔥 Top 10 Canciones Más Escuchadas")

top_10_songs = df.nlargest(10, 'plays')[['track', 'album', 'artist', 'plays']].copy()
top_10_songs['plays_formatted'] = top_10_songs['plays'].apply(format_plays)

col1, col2 = st.columns([2, 1])

with col1:
    fig_top10 = px.bar(
        top_10_songs,
        x='plays',
        y='track',
        orientation='h',
        color='album',
        title='Top 10 Canciones por Reproducciones',
        labels={'plays': 'Reproducciones', 'track': 'Canción', 'album': 'Álbum'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_top10.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500
    )
    st.plotly_chart(fig_top10, use_container_width=True)

with col2:
    st.subheader("Listado Top 10")
    for i, row in enumerate(top_10_songs.itertuples(), 1):
        st.markdown(f"**{i}. {row.track}**")
        st.caption(f"🎵 {row.album} | ▶️ {row.plays_formatted}")

st.markdown("---")

# ============= REPRODUCCIONES POR ÁLBUM =============
st.header("💿 Reproducciones Totales por Álbum")

album_stats = df.groupby('album').agg({
    'plays': 'sum',
    'track': 'count'
}).reset_index()
album_stats.columns = ['album', 'total_plays', 'num_tracks']
album_stats = album_stats.sort_values('total_plays', ascending=False)
album_stats['plays_formatted'] = album_stats['total_plays'].apply(format_plays)

fig_albums = px.bar(
    album_stats,
    x='album',
    y='total_plays',
    title='Reproducciones Totales por Álbum',
    labels={'total_plays': 'Reproducciones', 'album': 'Álbum'},
    color='total_plays',
    color_continuous_scale='Viridis'
)
fig_albums.update_layout(
    xaxis_tickangle=-45,
    height=500
)
st.plotly_chart(fig_albums, use_container_width=True)

st.markdown("---")

# ============= DETALLE POR ÁLBUM =============
st.header("📀 Detalle de Canciones por Álbum")

# Selector de álbum
albums_list = df['album'].unique().tolist()
selected_album = st.selectbox("Selecciona un álbum:", albums_list)

# Filtrar datos del álbum seleccionado
album_data = df[df['album'] == selected_album].sort_values('plays', ascending=False)

col1, col2 = st.columns([1, 3])

with col1:
    # Mostrar cover del álbum
    if selected_album in COVERS:
        st.image(COVERS[selected_album], caption=selected_album, width=200)
    
    # Estadísticas del álbum
    album_total_plays = album_data['plays'].sum()
    album_avg_plays = album_data['plays'].mean()
    album_num_tracks = len(album_data)
    
    st.markdown("### Estadísticas del Álbum")
    st.markdown(f"**Total reproducciones:** {format_plays(album_total_plays)}")
    st.markdown(f"**Promedio por canción:** {format_plays(album_avg_plays)}")
    st.markdown(f"**Número de canciones:** {album_num_tracks}")

with col2:
    # Gráfica de barras del álbum
    fig_album_detail = px.bar(
        album_data,
        x='track',
        y='plays',
        title=f'Canciones de "{selected_album}" ordenadas por reproducciones',
        labels={'plays': 'Reproducciones', 'track': 'Canción'},
        color='plays',
        color_continuous_scale='Blues'
    )
    fig_album_detail.update_layout(
        xaxis_tickangle=-45,
        height=450
    )
    st.plotly_chart(fig_album_detail, use_container_width=True)

# Tabla de canciones del álbum
st.subheader(f"Lista de canciones - {selected_album}")
album_table = album_data[['track', 'artist', 'plays', 'duration']].copy()
album_table['plays_formatted'] = album_table['plays'].apply(format_plays)
album_table = album_table.rename(columns={
    'track': 'Canción',
    'artist': 'Artistas',
    'plays_formatted': 'Reproducciones',
    'duration': 'Duración'
})
st.dataframe(
    album_table[['Canción', 'Artistas', 'Reproducciones', 'Duración']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ============= COMPARATIVA DE ÁLBUMES =============
st.header("📈 Comparativa de Álbumes")

col1, col2 = st.columns(2)

with col1:
    # Gráfico de pastel
    fig_pie = px.pie(
        album_stats,
        values='total_plays',
        names='album',
        title='Distribución de Reproducciones por Álbum',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Promedio de reproducciones por álbum
    album_avg = df.groupby('album')['plays'].mean().reset_index()
    album_avg.columns = ['album', 'avg_plays']
    album_avg = album_avg.sort_values('avg_plays', ascending=False)
    
    fig_avg = px.bar(
        album_avg,
        x='album',
        y='avg_plays',
        title='Promedio de Reproducciones por Canción (por Álbum)',
        labels={'avg_plays': 'Promedio', 'album': 'Álbum'},
        color='avg_plays',
        color_continuous_scale='Plasma'
    )
    fig_avg.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_avg, use_container_width=True)

st.markdown("---")

# ============= CANCIONES DE TODOS LOS ÁLBUMES =============
st.header("🎶 Todas las Canciones Ordenadas por Reproducciones")

# Selector de número de canciones a mostrar
num_songs = st.slider("Número de canciones a mostrar:", 10, len(df), 50)

all_songs_sorted = df.nlargest(num_songs, 'plays')[['track', 'album', 'artist', 'plays', 'duration']].copy()
all_songs_sorted['plays_formatted'] = all_songs_sorted['plays'].apply(format_plays)
all_songs_sorted['rank'] = range(1, len(all_songs_sorted) + 1)

# Mostrar tabla
st.dataframe(
    all_songs_sorted[['rank', 'track', 'album', 'artist', 'plays_formatted', 'duration']].rename(columns={
        'rank': '#',
        'track': 'Canción',
        'album': 'Álbum',
        'artist': 'Artistas',
        'plays_formatted': 'Reproducciones',
        'duration': 'Duración'
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Dashboard creado con amor para mis babuinos | Datos de discografía de Kanye West</p>
</div>
""", unsafe_allow_html=True)
