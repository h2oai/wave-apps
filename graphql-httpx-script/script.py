import collections
from asyncio import ensure_future, gather, get_event_loop_policy

from h2o_wave import data, site, ui
from httpx import AsyncClient

# TODO: Fill with yours.
GH_TOKEN = ""
TWITTER_BEARER_TOKEN = ""

graphql_query = """
fragment repoFields on Repository {
  createdAt
  description
  forkCount
  homepageUrl
  openGraphImageUrl
  stargazerCount
  licenseInfo {
    name
  }
  vulnerabilityAlerts {
    totalCount
  }
  watchers {
    totalCount
  }
  latestRelease {
    createdAt
  }
}

{
  Wave: repository(name: "wave", owner: "h2oai") {
    ...repoFields
  }
  Streamlit: repository(name: "streamlit", owner: "streamlit") {
    ...repoFields
  }
  Dash: repository(name: "dash", owner: "plotly") {
    ...repoFields
  }
  Shiny: repository(name: "shiny", owner: "rstudio") {
    ...repoFields
  }
}
"""


async def fill_github_issues(client: AsyncClient, framework, repo, org, data, query):
    query += f" repo:{org}/{repo}"
    # Use gather to make parallel calls and wait until both are complete.
    open_issues, closed_issues = await gather(
        client.get(
            url=f"https://api.github.com/search/issues",
            params={"q": f"{query} is:open"},
            headers={"Authorization": "Bearer " + GH_TOKEN},
        ),
        client.get(
            url=f"https://api.github.com/search/issues",
            params={"q": f"{query} is:closed"},
            headers={"Authorization": "Bearer " + GH_TOKEN},
        ),
    )
    data["bugs"].append([framework, "open", open_issues.json()["total_count"]])
    data["bugs"].append([framework, "closed", closed_issues.json()["total_count"]])


async def fill_github_data(client, data):
    # Make an HTTP Post request with JSON containing our query.
    res = await client.post(
        url="https://api.github.com/graphql",
        headers={"Authorization": "Bearer " + GH_TOKEN},
        json={"query": graphql_query},
    )
    # Unpack the response.
    data["github_data"] = res.json()["data"]
    # Fill the provided data dict for later consumption.
    for name, metadata in data["github_data"].items():
        data["vulnerabilities"].append(
            [name, metadata["vulnerabilityAlerts"]["totalCount"]]
        )
        data["watchers"].append([name, metadata["watchers"]["totalCount"]])
        data["stars"].append([name, metadata["stargazerCount"]])


async def fill_twitter_data(client, framework, data):
    res = await client.get(
        url="https://api.twitter.com/2/tweets/counts/recent",
        headers={"Authorization": "Bearer " + TWITTER_BEARER_TOKEN},
        params={"query": framework},
    )
    data["twitter_data"].append([framework, res.json()["meta"]["total_tweet_count"]])


async def fill_stackoverflow_data(client, tag, data):
    res = await client.get(
        f"https://api.stackexchange.com/2.2/tags?inname={tag}&site=stackoverflow"
    )
    data["so_data"].append([tag, res.json()["items"][0]["count"]])


# Register page at "/" route.
page = site["/"]


async def main():
    # Setup layout.
    page["meta"] = ui.meta_card(
        box="",
        title="Wave comparison",
        layouts=[
            ui.layout(
                breakpoint="xs",
                zones=[
                    ui.zone(name="header"),
                    ui.zone(name="intro", direction=ui.ZoneDirection.ROW, size="500px"),
                    ui.zone(
                        name="plots1", direction=ui.ZoneDirection.ROW, size="300px"
                    ),
                    ui.zone(
                        name="plots2", direction=ui.ZoneDirection.ROW, size="300px"
                    ),
                ],
            ),
        ],
    )

    # Render header.
    page["header"] = ui.header_card(
        box="header",
        title="Wave competition comparison",
        subtitle="Let's see how well Wave does against its rivals.",
        image="https://wave.h2o.ai/img/h2o-logo.svg",
    )

    # Fetch data.
    plot_data = collections.defaultdict(list)
    async with AsyncClient() as client:
        label_query = "is:issue label:bug"
        title_query = "bug in:title"
        await gather(
            ensure_future(fill_github_data(client, plot_data)),
            ensure_future(
                fill_github_issues(
                    client, "H2O Wave", "wave", "h2oai", plot_data, label_query
                )
            ),
            ensure_future(
                fill_github_issues(
                    client,
                    "Streamlit",
                    "streamlit",
                    "streamlit",
                    plot_data,
                    label_query,
                )
            ),
            ensure_future(
                fill_github_issues(
                    client, "Plotly Dash", "dash", "plotly", plot_data, title_query
                )
            ),
            ensure_future(
                fill_github_issues(
                    client, "R Shiny", "shiny", "rstudio", plot_data, "bug"
                )
            ),
            ensure_future(fill_twitter_data(client, "H2O Wave", plot_data)),
            ensure_future(fill_twitter_data(client, "Streamlit", plot_data)),
            ensure_future(fill_twitter_data(client, "Plotly Dash", plot_data)),
            ensure_future(fill_twitter_data(client, "R Shiny", plot_data)),
            ensure_future(fill_stackoverflow_data(client, "h2o-wave", plot_data)),
            ensure_future(fill_stackoverflow_data(client, "streamlit", plot_data)),
            ensure_future(fill_stackoverflow_data(client, "plotly-dash", plot_data)),
            ensure_future(fill_stackoverflow_data(client, "shiny", plot_data)),
        )

    # Render overview cards for every framework.
    for name, metadata in plot_data["github_data"].items():
        latest_release = None
        if metadata["latestRelease"] != None:
            latest_release = metadata["latestRelease"]["createdAt"]
        page[f"overview-{name}"] = ui.tall_article_preview_card(
            box=ui.box("intro", width="25%"),
            title=name,
            subtitle=metadata["licenseInfo"]["name"],
            image=metadata["openGraphImageUrl"],
            content=f"""
{metadata['description']}
</br></br>
**Created**: {metadata['createdAt'].split('T')[0]}
</br>
**Last release**: {latest_release.split('T')[0] if latest_release else 'Unknown'}
</br>
**Homepage**: {metadata['homepageUrl']}
            """,
        )

    # Render plots.
    page["bugs"] = ui.plot_card(
        box=ui.box("plots1", width="25%", order=1),
        title="Bugs",
        data=data("framework state bugs", 4, rows=plot_data["bugs"], pack=True),
        plot=ui.plot(
            [
                ui.mark(
                    type="interval",
                    x="=framework",
                    y="=bugs",
                    color="=state",
                    dodge="auto",
                    color_range="$red $green",
                    y_min=0,
                )
            ]
        ),
    )

    page["watchers"] = ui.plot_card(
        box=ui.box("plots1", width="25%", order=2),
        title="Watchers",
        data=data("framework watchers", 4, rows=plot_data["watchers"], pack=True),
        plot=ui.plot(
            [
                ui.mark(
                    type="interval",
                    x="=framework",
                    y="=watchers",
                    y_min=0,
                    fill_color="$green",
                )
            ]
        ),
    )

    page["stars"] = ui.plot_card(
        box=ui.box("plots1", width="25%", order=3),
        title="Stars",
        data=data("framework stars", 4, rows=plot_data["stars"], pack=True),
        plot=ui.plot(
            [
                ui.mark(
                    type="interval",
                    x="=framework",
                    y="=stars",
                    y_min=0,
                    fill_color="$yellow",
                )
            ]
        ),
    )

    page["vulnerabilities"] = ui.plot_card(
        box=ui.box("plots1", width="25%", order=4),
        title="Vulnerabilities",
        data=data("framework vulns", 4, rows=plot_data["vulnerabilities"], pack=True),
        plot=ui.plot([ui.mark(type="interval", x="=framework", y="=vulns", y_min=0)]),
    )

    page["stackoverflow"] = ui.plot_card(
        box="plots2",
        title="Stack overflow questions",
        data=data("framework questions", 4, rows=plot_data["so_data"], pack=True),
        plot=ui.plot(
            [
                ui.mark(
                    type="interval",
                    x="=framework",
                    y="=questions",
                    y_min=0,
                    fill_color="$orange",
                )
            ]
        ),
    )

    page["twitter"] = ui.plot_card(
        box="plots2",
        title="Twitter tweets for the past week",
        data=data("framework tweets", 4, rows=plot_data["twitter_data"], pack=True),
        plot=ui.plot(
            [
                ui.mark(
                    type="interval",
                    x="=framework",
                    y="=tweets",
                    y_min=0,
                    fill_color="$blue",
                )
            ]
        ),
    )

    page.save()


# Run within asyncio event loop to allow concurrent HTTP calls.
loop = get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
