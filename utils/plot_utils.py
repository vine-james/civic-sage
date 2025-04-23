
from utils.constants import ChartTypes
import plotly.graph_objects as go
from shapely.geometry import mapping
import streamlit as st
import geopandas as gpd

palettes = {
    "sequential": ["#fee0d2", "#fcae91", "#fb6a4a", "#cb181d", "#67000d"],
    "categorical": ["#2171b5", "#E07941", "#8456ce", "#c33d69", "#6BAE13", "#096f64"],
    "pos-neu-neg": ["#2ecc71", "#7f8c8d", "#e74c3c"],
    "highlight": ["#d7191c"],
  }

colour_gridlines = "#ebebeb"
colour_ticks = "#787878"

colour_offblack = "#0d0d0d"
colour_offwhite = "#e4e4e4"

colour_grey = "#7f8c8d"

ticks_size = 12 # 14
title_size = 24
axis_title_size = title_size * 0.65 # Superscript sizes the text by 65%
annotation_size = 16 # Size of hoverlabel text & any annotations

font = "Outfit, sans-serif"

line_thickness_standard = 3
line_thickness_highlight = 5

footnote_x_pos = -0.007
footnote_y_pos = -0.19


def get_colour_palette(palette_type="sequential", num_colours=6):
    """
    Return a palette of colours for use in charts, selected from palette and separation based on number of colours needed - palette size
    """
    chosen_palette = palettes[palette_type]

    # Max of 6 colors (or however many put in palettes - need to keep note of)
    num_colours = min(num_colours, len(chosen_palette))

    if num_colours > 1:
      indices = [int(i * (len(chosen_palette) - 1) / (num_colours - 1)) for i in range(num_colours)]
      selected_colours = [chosen_palette[i] for i in indices]
    else:
      selected_colours = [chosen_palette[0]]

    return selected_colours


def update_fig_style(fig, chart_title, footnote, chart_type, yaxis_title, xaxis_title, grouped_plot, num_yticks, num_xticks, ticks_size, legend, gdf, has_subplots):
    """
    Update figure according to a master-style for all charts
    """

    fig.update_xaxes(
        anchor="free",
        ticks="outside",
        ticklen=5,
        tickfont=dict(color=colour_ticks, size=ticks_size),
        title_standoff=50,
        nticks=num_xticks + 1,
        title_text="", # Remove natural title so that we can replace it with an annotation. Doing this because Plotly doesn't seem to allow you to easily move the X axis title.
    )

    fig.update_yaxes(
        gridcolor=colour_gridlines,
        tickfont=dict(color=colour_ticks, size=ticks_size), #size=16
        title_text="", # Remove natural title so that we can replace it with a subscript in title. Doing this because Plotly currently doesn't allow you to rotate title 90 degrees.
        nticks=num_yticks + 1 # For some reason, only shows -1 the correct amount
    )

    # If X axes title, set via an annotation
    if xaxis_title:
        fig.update_layout(
            annotations=[
                dict(
                    x=0.5,
                    y=-0.135,
                    text=xaxis_title,
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    font=dict(size=axis_title_size, family=font, color=colour_ticks)
                )
            ]
        )

    # Recolor the tick text, lines and ticks themselves
    fig.update_layout(
        xaxis=dict(
            tickcolor=colour_ticks,
            tickfont=dict(color=colour_ticks),
            linecolor=colour_ticks,
        ),
        yaxis=dict(
            tickfont=dict(color=colour_ticks),
            linecolor="white",
            tickwidth=0,
            linewidth=0,
            showgrid=False,
        )
    )

    # Set the y position of the title. Alter if an active Y axis title, and/or if there is a legend.
    title_y_pos = 0.8
    top_margin = 60
    
    if legend:
        title_y_pos += 0.1
        top_margin += 20
    if yaxis_title:
        title_y_pos += 0.1
        top_margin += 20

    if has_subplots:
        title_y_pos += 0.1
        top_margin += 20

    # Update title style & gridlines
    fig.update_layout(
        title=dict(
            text=f"{chart_title}<br><sup style='color:{colour_ticks}; font-weight:normal'>{yaxis_title}</sup>",
            font=dict(
                size=title_size,
                family=font,
                color=colour_offblack,
            ),
            xref="container",
            yref="container",
            x=0.02,
            y=0.95,
            yanchor="top",
            xanchor="left",
        ),
        xaxis=dict(gridcolor=colour_gridlines),
        yaxis=dict(gridcolor=colour_gridlines),
    )

    # Update overall style & axes
    fig.update_layout(
        font=dict(family=font),
        margin=dict(t=top_margin, l=20, b=60),
        yaxis=dict(
            side="left",
            ticks="outside",
            ticklen=0,
            tickwidth=0,
            linewidth=0,
            showgrid=True,
            nticks=5,
        ),
        xaxis=dict(
            ticks="outside",
            ticklen=5,
            title_standoff=50,
            showgrid=False,
            linecolor=colour_ticks,
            tickcolor=colour_ticks,
            anchor="free",
            tickfont=dict(color=colour_ticks, size=ticks_size), #size=16
        )
    )

    # Fix styling issues for sub-plots if they are present
    if has_subplots:
        for axis_key in fig.layout:
            if axis_key.startswith("xaxis"):
                fig.layout[axis_key].update(
                    dict(
                        ticklen=5,
                        anchor="free",
                        ticks="outside",
                        tickfont=dict(color=colour_ticks, size=ticks_size),
                        title_standoff=50,
                        nticks=num_xticks + 1,
                        # title_text="", # Remove natural title so that we can replace it with an annotation. Doing this because Plotly doesn't seem to allow you to easily move the X axis title.
                        showgrid=False,
                        linecolor=colour_ticks,
                        tickcolor=colour_ticks,
                    )
                )
            elif axis_key.startswith("yaxis"):
                fig.layout[axis_key].update(
                    dict(
                        side="left",
                        ticks="outside",
                        ticklen=0,
                        tickwidth=0,
                        linewidth=0,
                        showgrid=True,
                    )
                )

    # Chart-type-specific behaviour
    if chart_type == ChartTypes.LINE:
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b>:   %{y}<extra></extra>",
        )
        # Apply to charts with line subplots
        fig.update_traces(line=dict(width=line_thickness_standard, dash="solid"), selector=dict(type="scatter", mode="lines"))


    elif chart_type == ChartTypes.CHOROPLETH:
        # Calculate/plot outer boundary lines
        outer_boundary = gdf.unary_union  # Combine all geometries into one boundary
        boundary_geojson = mapping(outer_boundary)
        boundary_coords = list(boundary_geojson["coordinates"][0])  # Assuming a single polygon

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=[coord[0] for coord in boundary_coords],
            lat=[coord[1] for coord in boundary_coords],
            line=dict(width=2, color="black"),
            name="",
            hoverinfo="skip",
        ))

        fig.update_traces(marker_line_width=1.5, marker_line_color="white", selector=dict(type="choroplethmapbox"))

        # Set overall mapbox style
        fig.update_layout(
            margin=dict(t=55),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            # mapbox_style="white-bg",
        )

    elif chart_type == ChartTypes.SCATTER:
        pass

    elif chart_type == ChartTypes.BAR:
        pass

    else:
        # If no other type of chart requiring specific behaviour
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>")
        

    # Set black hoverlabel
    fig.update_layout(
        hoverlabel=dict(
            bgcolor=colour_offblack,
            font_size=annotation_size,
            font_color=colour_offwhite,
        )
    )

    # Set footnote as an annotation outside of axes
    # Check that footnote isn't intentionally blank
    if footnote:
        footnote_y_pos = -0.19
        if chart_type == ChartTypes.CHOROPLETH:
            footnote_y_pos += 0.12

        fig.add_annotation(
            x=-0.007,
            y=footnote_y_pos,
            xref="paper",
            yref="paper",
            text=f"<b>(!)</b>  {footnote}",
            showarrow=False,
            font=dict(
                size=ticks_size,
                family=font,
                color=colour_ticks
            )
        )

    # Set Legend if applicable
    if legend:
        fig.update_layout(
            showlegend=True,
            legend_title=None,
            legend=dict(
                x=0,
                y=1,
                xanchor="left",
                yanchor="bottom",
                orientation="h",
                font=dict(
                    family=font,
                    size=annotation_size,
                )
            )
        )

    else:
        fig.update_layout(
            showlegend=False
        )


    # Group all lines together in hoverplot + color the hoverplot name accordingly
    if grouped_plot:
        fig.update_layout(hovermode="x unified")
        fig.update_xaxes(showspikes=True, spikecolor="rgb(203,193,185)", spikesnap="cursor", spikemode="across", spikethickness=3, spikedash="dot")
        for plot in fig["data"]:
                plot["name"] = f"<b><span style='color:{plot['marker']['color']}'>{plot['name']}</span></b>"


    return fig


def style_plotly_chart(
        fig,
        chart_title,
        footnote=None,
        chart_type=ChartTypes.OTHER,
        yaxis_title=None,
        xaxis_title=None,
        grouped_plot=False,
        num_yticks=5,
        num_xticks=5,
        ticks_size=ticks_size,
        legend=None,
        gdf=None, # Needed for creating outer boundaries on choropleths
        has_subplots=False,
    ):
    """
    Utility function to update figure style & embed in streamlit page
    """
    fig = update_fig_style(fig, chart_title, footnote, chart_type, yaxis_title, xaxis_title, grouped_plot, num_yticks, num_xticks, ticks_size, legend, gdf, has_subplots)

    # fig.show()
    st.plotly_chart(fig, use_container_width=True)
    return fig



# CHARTS
def plot_sessions_by_ward(df, mp_name, constituency):

    df.rename(columns={"Ward Code": "WD24CD"}, inplace=True)

    gdf = gpd.read_file(f"files/maps/{constituency}.geojson")

    gdf_merged = gdf.merge(df, on="WD24CD", how='left')
    gdf_merged = gdf_merged.to_crs(epsg=4326)

    colour_palette = get_colour_palette(palette_type="sequential")
    i_scale = 1 / len(colour_palette)
    current_i = 0.0000000001
    palette_scale = []

    for colour in colour_palette:
        palette_scale.append([current_i, colour])
        current_i += i_scale

    palette_scale.insert(0, [0, "black"])
    palette_scale[-1][0] = 1

    fig = go.Figure(go.Choroplethmapbox(
            geojson=gdf_merged.__geo_interface__, 
            locations=gdf_merged["WD24CD"],
            z=gdf_merged["Sessions"],
            marker_opacity=0.5,
            marker_line_width=1,
            featureidkey="properties.WD24CD",
            text=gdf_merged["Ward"],
            hovertemplate="<b>Ward</b>: %{text}<br>%{z}<extra></extra>",
            colorscale=palette_scale,
        ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10.1,
        mapbox_center={"lat": gdf_merged.geometry.centroid.y.mean(),
                   "lon": gdf_merged.geometry.centroid.x.mean()},
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    style_plotly_chart(
        fig=fig,
        chart_title="Unique Sessions by Ward",
        chart_type=ChartTypes.CHOROPLETH,
        yaxis_title=f"Sessions from outside of Constituency: {df[df['Ward'] == 'Outside']['Sessions'].iloc[0]}",
        gdf=gdf,
        footnote="A unique session may not always equate to a unique user.",
    )


def plot_political_knowledge_by_ward(df, mp_name, constituency):
    option = st.selectbox(
        "Select a topic",
        ["UK Politics", "UK Government", "UK Parliament"]
    )

    rating_map = {
        0: "No data available",
        1: "1: Nothing at all",
        2: "2: Not very much",
        3: "3: A fair amount",
        4: "4: A great deal",
    }

    df.rename(columns={"Ward Code": "WD24CD"}, inplace=True)
    df["Rating"] = df[option].map(rating_map)

    gdf = gpd.read_file(f"files/maps/{constituency}.geojson")

    gdf_merged = gdf.merge(df, on="WD24CD", how='left')
    gdf_merged = gdf_merged.to_crs(epsg=4326)


    colour_palette = get_colour_palette(palette_type="sequential")
    i_scale = 1 / len(colour_palette)
    current_i = 0.0000000001
    palette_scale = []

    for colour in colour_palette:
        palette_scale.append([current_i, colour])
        current_i += i_scale

    palette_scale.insert(0, [0, "black"])
    palette_scale[-1][0] = 1

    fig = go.Figure(go.Choroplethmapbox(
            geojson=gdf_merged.__geo_interface__, 
            locations=gdf_merged["WD24CD"],
            z=gdf_merged[option],
            marker_opacity=0.5,
            marker_line_width=1,
            featureidkey="properties.WD24CD",
            text=gdf_merged["Ward"],
            customdata=gdf_merged["Rating"],
            hovertemplate="<b>Ward</b>: %{text}<br>%{customdata}<extra></extra>",
            colorscale=palette_scale,
            zmin=0,
            zmax=4,
        ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10.1,
        mapbox_center={"lat": gdf_merged.geometry.centroid.y.mean(),
                   "lon": gdf_merged.geometry.centroid.x.mean()},
        margin={"r":0,"t":0,"l":0,"b":0},
    )

    fig.update_coloraxes(colorbar_dtick=1)

    style_plotly_chart(
        fig=fig,
        chart_title=f"Average knowledge of {option} by Ward",
        chart_type=ChartTypes.CHOROPLETH,
        yaxis_title=f"Average from outside of Constituency: {df[df['Ward'] == 'Outside']['Rating'].iloc[0]}",
        gdf=gdf,
        footnote="'Knowledge' as self-described on a rating of 1-4, accompanied by descriptive labels presented.",
    )


def plot_conversations_by_hour(df, mp_name, constituency):
    fig = go.Figure()

    df = df.pivot(index="Time Period", columns="Constituency", values="Count").fillna(0).reset_index()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Bar(
        x=df["Time Period"],
        y=df["Inside"],
        hovertemplate=f"<b>{constituency} Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[0]
    ))

    fig.add_trace(go.Bar(
        x=df["Time Period"],
        y=df["Outside"],
        hovertemplate=f"<b>Other Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[1]
    ))

    fig.update_layout(
        barmode="stack",
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"",
        chart_title=f"<span style='font-size: 18px'>Total <span style='color: {colours[0]};'>Constituents</span> & <span style='color: {colours[1]}'>Other Users</span> Sessions by Time of Day</span>",
        chart_type=ChartTypes.BAR,
    )


def plot_conversations_by_length(df, mp_name, constituency):
    fig = go.Figure()
    
    df = df.pivot(index="Session Length", columns="Constituency", values="Count").fillna(0).reset_index()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Bar(
        x=df["Session Length"],
        y=df["Inside"],
        hovertemplate=f"<b>{constituency} Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[0]
    ))

    fig.add_trace(go.Bar(
        x=df["Session Length"],
        y=df["Outside"],
        hovertemplate=f"<b>Other Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[1]
    ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            categoryorder="array",
            categoryarray=["Less than 1 minute", "1-5 minutes", "5-15 minutes", "15-30 minutes", "30 minutes to 1 hour", "1 hour+"] 
        )
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"",
        chart_title=f"<span style='font-size: 18px'>Total <span style='color: {colours[0]};'>Constituents</span> & <span style='color: {colours[1]}'>Other Users</span> Sessions by Length of Session</span>",
        chart_type=ChartTypes.BAR,
    )


def plot_conversations_by_messages(df, mp_name, constituency):
    fig = go.Figure()
    
    df = df.pivot(index="Message Count Category", columns="Constituency", values="Count").fillna(0).reset_index()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Bar(
        x=df["Message Count Category"],
        y=df["Inside"],
        hovertemplate=f"<b>{constituency} Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[0]
    ))

    fig.add_trace(go.Bar(
        x=df["Message Count Category"],
        y=df["Outside"],
        hovertemplate=f"<b>Other Users</b>: "+"%{y}<extra></extra>",
        marker_color=colours[1]
    ))

    fig.update_layout(
        barmode="stack",
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="Sessions",
        xaxis_title="Messages",
        chart_title=f"<span style='font-size: 18px'>Total <span style='color: {colours[0]};'>Constituents</span> & <span style='color: {colours[1]}'>Other Users</span> Sessions by Number of Messages</span>",
        chart_type=ChartTypes.BAR,
    )




def plot_sessions_by_day(df, mp_name, constituency):
    fig = go.Figure()

    df = df.pivot(index="Session Date", columns="Constituency", values="Sessions").fillna(0).reset_index()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Scatter(
        x=df["Session Date"],
        y=df["Inside"],
        name=f"{constituency} Users",
        marker_color=colours[0]
    ))

    fig.add_trace(go.Scatter(
        x=df["Session Date"],
        y=df["Outside"],
        name=f"Other Users",
        marker_color=colours[1]
    ))

    fig.update_layout(
        xaxis_tickformat="%b %d",
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"",
        chart_title=f"<span style='font-size: 18px'>Total <span style='color: {colours[0]};'>Constituents</span> & <span style='color: {colours[1]}'>Other Users</span> Sessions by Day of Month</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
    )


def plot_median_sentiment_by_day(df, mp_name, constituency):
    option = st.selectbox(
        "Select an audience",
        ["Constituents", "Other Users"],
        key="Sentiment",
    )

    option_map = {
        "Constituents": "Inside",
        "Other Users": "Outside",
    }
    
    fig = go.Figure()

    df_selected = df[df["Constituency"] == option_map[option]]
    colours = get_colour_palette(palette_type="pos-neu-neg", num_colours=3)

    categories = ["Positive", "Neutral", "Negative"]

    for i, category in enumerate(categories):
        fig.add_trace(go.Scatter(
            x=df_selected["Session Date"],
            y=df_selected[category],
            fill="tonexty",
            name=category,
            mode="lines",
            marker=dict(color=colours[i]),
            stackgroup="one",
        ))

    fig.update_layout(
        yaxis=dict(
            type="linear",
            range=[0, 1],
            tickformat=".0%",
            dtick=0.2,
        ),
        xaxis_tickformat="%b %d",
        
    ),

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"Sentiment share of message (%)",
        chart_title=f"<span style='font-size: 18px'>Median <span style='color: {colours[0]};'>Positive</span>, <span style='color: {colours[1]};'>Neutral</span> & <span style='color: {colours[2]};'>Negative</span> Sentiment by Day of Month for {option}</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
    )


def plot_median_stance_by_day(df, mp_name, constituency):
    option = st.selectbox(
        "Select an audience",
        ["Constituents", "Other Users"],
        key="Stance",
    )

    option_map = {
        "Constituents": "Inside",
        "Other Users": "Outside",
    }
    
    fig = go.Figure()

    df_selected = df[df["Constituency"] == option_map[option]]
    colours = get_colour_palette(palette_type="pos-neu-neg", num_colours=3)

    categories = ["Supportive", "Neutral", "Oppositional"]

    for i, category in enumerate(categories):

        fig.add_trace(go.Scatter(
            x=df_selected["Session Date"],
            y=df_selected[category],
            fill="tonexty",
            name=category,
            mode="lines",
            marker=dict(color=colours[i]),
            stackgroup="one",
        ))

    fig.update_layout(
        yaxis=dict(
            type="linear",
            range=[0, 1],
            tickformat=".0%",
            dtick=0.2,
        ),
        xaxis_tickformat="%b %d",
    ),

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"Stance share of message (%)",
        chart_title=f"<span style='font-size: 18px'>Median <span style='color: {colours[0]};'>Supportive</span>, <span style='color: {colours[1]};'>Neutral</span> & <span style='color: {colours[2]};'>Oppositional</span> Stance by Day of Month for {option}</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
    )



def plot_median_ideology_by_day(df, mp_name, constituency):
    option = st.selectbox(
        "Select an audience",
        ["Constituents", "Other Users"],
        key="Ideology",
    )

    option_map = {
        "Constituents": "Inside",
        "Other Users": "Outside",
    }
    
    fig = go.Figure()

    df_selected = df[df["Constituency"] == option_map[option]]
    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    categories = ["Far-left", "Center-left", "Centrist", "Center-right", "Far-right"]

    for i, category in enumerate(categories):

        fig.add_trace(go.Scatter(
            x=df_selected["Session Date"],
            y=df_selected[category],
            fill="tonexty",
            name=category,
            mode="lines",
            marker=dict(color=colours[i]),
            stackgroup="one",
        ))

    fig.update_layout(
        yaxis=dict(
            type="linear",
            range=[0, 1],
            tickformat=".0%",
            dtick=0.2,
        ),
        xaxis_tickformat="%b %d",
    ),

    style_plotly_chart(
        fig=fig,
        yaxis_title=f"Ideological scoring share of message (%)",
        chart_title=f"<span style='font-size: 18px'>Median <span style='color: {colours[0]};'>FL</span>, <span style='color: {colours[1]};'>CL</span>, <span style='color: {colours[2]};'>C</span>, <span style='color: {colours[3]};'>CR</span>, <span style='color: {colours[4]};'>FR</span> Ideological Scores by Day of Month for {option}</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
        footnote="FL, CL, C, CR, FR = Far-left, Center-left, Centrist, Center-right, Far-right",
    )


def plot_top_keywords_by_week(df, mp_name, constituency):
    option = st.selectbox(
        "Select an audience",
        ["Constituents", "Other Users"],
        key="Top Keywords",
    )

    option_map = {
        "Constituents": "Inside",
        "Other Users": "Outside",
    }
    
    df_selected = df[df["Constituency"] == option_map[option]]
    pivot_df = df_selected.groupby(["Week", "Top Keyword"])["Count"].sum().reset_index()
    weeks = sorted(df_selected["Week"].unique())

    fig = go.Figure()
    colours = get_colour_palette("categorical", num_colours=6)

    for week in weeks:
        week_df = pivot_df[pivot_df["Week"] == week]
        keywords = week_df["Top Keyword"].tolist()
        counts = week_df["Count"].tolist()
        percents = [100 * c / sum(counts) if sum(counts) > 0 else 0 for c in counts]

        for percent, keyword, color in zip(percents, keywords, colours):
            if keyword == "No data available":
                color = colour_grey
            
            fig.add_bar(
                x=[week],
                y=[percent],
                name=keyword,
                marker_color=color,
                text=[keyword],
                textposition="inside",
                textfont=dict(color="white", size=12),
                insidetextanchor="middle",
                hovertemplate=f"<b>Keyword</b>: {keyword}<br><b>Share</b>: {percent:.1f}%<extra></extra>",
            )

    fig.update_layout(
        barmode="stack",
        yaxis=dict(ticksuffix="%", dtick=20)
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="Keyword Share (%)",
        xaxis_title="Week",
        chart_title=f"<span style='font-size: 18px'>Top 5 User Keywords by Week for {option}</span>",
        chart_type=ChartTypes.BAR,
        footnote=f"Keywords are derived from ranked analysis of all {option} messages (anonymised) for that time period."
    )


def plot_top_web_keywords_by_week(df, mp_name, constituency):
    option = st.selectbox(
        "Select an audience",
        ["Constituents", "Other Users"],
        key="Top Web Keywords",
    )

    option_map = {
        "Constituents": "Inside",
        "Other Users": "Outside",
    }
    
    df_selected = df[df["Constituency"] == option_map[option]]
    pivot_df = df_selected.groupby(["Week", "Top Keyword"])["Count"].sum().reset_index()
    weeks = sorted(df_selected["Week"].unique())

    fig = go.Figure()
    colours = get_colour_palette("categorical", num_colours=6)

    for week in weeks:
        week_df = pivot_df[pivot_df["Week"] == week]
        keywords = week_df["Top Keyword"].tolist()
        counts = week_df["Count"].tolist()
        percents = [100 * c / sum(counts) if sum(counts) > 0 else 0 for c in counts]

        for percent, keyword, color in zip(percents, keywords, colours):
            if keyword == "No data available":
                color = colour_grey
            
            fig.add_bar(
                x=[week],
                y=[percent],
                name=keyword,
                marker_color=color,
                text=[keyword],
                textposition="inside",
                textfont=dict(color="white", size=12),
                insidetextanchor="middle",
                hovertemplate=f"<b>Keyword</b>: {keyword}<br><b>Share</b>: {percent:.1f}%<extra></extra>",
            )

    fig.update_layout(
        barmode="stack",
        yaxis=dict(ticksuffix="%", dtick=20)
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="Keyword Share (%)",
        xaxis_title="Week",
        chart_title=f"<span style='font-size: 18px'>Top 5 AI Websearch Keywords by Week for {option}</span>",
        chart_type=ChartTypes.BAR,
        footnote=f"Keywords are derived from ranked analysis of all AI websearch responses from {option} prompts for that time period."
    )


def plot_reported_responses_by_day(df, mp_name, constituency):
    fig = go.Figure()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Scatter(
        x=df["Report Date"],
        y=df["Response"],
        name="Reports",
        marker_color=colours[0]
    ))

    fig.update_layout(
        xaxis_tickformat="%b %d",
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="",
        chart_title="<span style='font-size: 18px'>Total Reported Responses by Day of Month</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
    )


def plot_sensitive_messages_by_day(df, mp_name, constituency):
    fig = go.Figure()

    colours = get_colour_palette(palette_type="categorical", num_colours=6)

    fig.add_trace(go.Scatter(
        x=df["Session Date"],
        y=df["Count"],
        name="Flagged Messages",
        marker_color=colours[0]
    ))

    fig.update_layout(
        xaxis_tickformat="%b %d",
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="",
        chart_title="<span style='font-size: 18px'>Total Sensitive Messages by Day of Month</span>",
        chart_type=ChartTypes.LINE,
        grouped_plot=True,
        footnote="'User prompts flagged by Civic Sage as 'sensitive', where user is re-directed e.g. to 999 / local health services."
    )


def plot_top_keywords_reports_by_week(df, mp_name, constituency):
    pivot_df = df.groupby(["Week", "Top Keyword"])["Count"].sum().reset_index()
    weeks = sorted(df["Week"].unique())

    fig = go.Figure()
    colours = get_colour_palette("categorical", num_colours=6)

    for week in weeks:
        week_df = pivot_df[pivot_df["Week"] == week]
        keywords = week_df["Top Keyword"].tolist()
        counts = week_df["Count"].tolist()
        percents = [100 * c / sum(counts) if sum(counts) > 0 else 0 for c in counts]

        for percent, keyword, color in zip(percents, keywords, colours):
            if keyword == "No data available":
                color = colour_grey
            
            fig.add_bar(
                x=[week],
                y=[percent],
                name=keyword,
                marker_color=color,
                text=[keyword],
                textposition="inside",
                textfont=dict(color="white", size=12),
                insidetextanchor="middle",
                hovertemplate=f"<b>Keyword</b>: {keyword}<br><b>Share</b>: {percent:.1f}%<extra></extra>",
            )

    fig.update_layout(
        barmode="stack",
        yaxis=dict(ticksuffix="%", dtick=20)
    )

    style_plotly_chart(
        fig=fig,
        yaxis_title="Keyword Share (%)",
        xaxis_title="Week",
        chart_title=f"<span style='font-size: 18px'>Top 5 Keywords for Reported AI Responses by Week</span>",
        chart_type=ChartTypes.BAR,
        footnote=f"Keywords are derived from ranked analysis of all reported AI messages for that time period."
    )
