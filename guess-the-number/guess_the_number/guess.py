import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import randint
from typing import Dict, List

# don't forget to import main below
# Read https://h2oai.github.io/wave/docs/tutorial-counter#step-1-start-listening
from h2o_wave import Q, app, main, ui


@dataclass
class WaveColors:
    # Colors from Wave default Theme.
    red: str = '#F44336'
    pink: str = '#E91E63'
    purple: str = '#9C27B0'
    violet: str = '#673AB7'
    indigo: str = '#3F51B5'
    blue: str = '#2196F3'
    azure: str = '#03A9F4'
    cyan: str = '#00BCD4'
    teal: str = '#009688'
    mint: str = '#4CAF50'
    green: str = '#8BC34A'
    lime: str = '#CDDC39'
    yellow: str = '#FFEB3B'
    amber: str = '#FFC107'
    orange: str = '#FF9800'
    tangerine: str = '#FF5722'
    brown: str = '#795548'
    gray: str = '#9E9E9E'


@dataclass
class Game:
    player_id: str
    is_public: bool = field(default=False)
    game_id: str = field(init=False)
    status: str = field(init=False)
    number: int = field(init=False)
    start_time: datetime = field(init=False)
    end_time: datetime = field(init=False)
    guesses: List[int] = field(init=False, default_factory=list)
    guess_times: List[timedelta] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.game_id = str(uuid.uuid4())
        self.status = 'playing'
        self.number = randint(1, 100)
        self.start_time = datetime.now()
        self.end_time = self.start_time

    def guess(self, value: int) -> str:
        self.guesses.append(value)
        self.guess_times.append(datetime.now() - self.start_time)
        if value < self.number:
            return 'Go Higher 👍'
        elif value > self.number:
            return 'Go Lower 👎'
        self.end_time = datetime.now()
        self.status = 'done'
        return 'You Got It!'

    def game_time(self):
        duration = self.end_time - self.start_time
        days = duration.days
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = (
            f'**{seconds}** Seconds, and **{duration.microseconds}** Microseconds'
        )
        if minutes > 0:
            time_str = f'**{minutes}** Minutes, ' + time_str
        if hours > 0:
            time_str = f'**{hours}** Hours, ' + time_str
        if days > 0:
            time_str = f'**{days}** Days, ' + time_str
        return time_str

    def time_seconds(self):
        if not self.guess_times:
            return 0
        duration = self.guess_times[-1]
        return round(duration.seconds + duration.microseconds / 1e6, 4)


@dataclass
class Player:
    email: str
    player_id: str
    first: str = field(init=False, default='hacker')
    last: str = field(init=False, default='')
    name: str = field(init=False, default='hacker')
    games: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        names = self.email.split('@')[0].split('.')
        if len(names) > 1:
            self.first, *_, self.last = names
        elif names:
            self.first = names[0]
        self.name = f'{self.first} {self.last}'.title()

    def private_games(self):
        return [x for x in self.games.values() if not x.is_public]

    def games_in_progress(self):
        return [x for x in self.games.values() if x.status != 'done']


async def start_new_game(q: Q):
    q.client.game = Game(q.user.player.player_id)
    q.user.player.games[q.client.game.game_id] = q.client.game

    q.page['starting_game'] = ui.form_card(
        box='4 4 3 3',
        items=[
            ui.text_l('I am thinking of a number between 1 and 100'),
            ui.text_m('can you guess what it is?'),
            ui.text_xs('⠀'),
            ui.slider(
                name='guess',
                label='your guess',
                min=1,
                max=100,
                value=100,
                trigger=True,
            ),
            ui.text_xs('⠀'),
            ui.buttons(
                items=[ui.button(name='quit_game', label='Quit', primary=True)],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_base_ui(q):
    q.page['meta'] = ui.meta_card(box='', title='Guess the Number')
    q.page['title'] = ui.header_card(
        box='1 1 3 1',
        title='Guess the Number',
        subtitle='',
        icon='ChatBot',
        icon_color=WaveColors.cyan,
    )
    q.page['user'] = ui.header_card(
        color='card',
        box='4 1 6 1',
        title=f'Player Name : {q.user.player.first} {q.user.player.last}'.title(
        ),
        subtitle='',
        icon='PlayerSettings',
        icon_color=WaveColors.cyan,
        items=[
            ui.toggle(name='toggle_theme',
                      label='Dark theme', trigger=True),
        ],
    )

    await q.page.save()


async def make_welcome_card(q):
    q.page['hello'] = ui.form_card(
        box='4 4 3 3',
        items=[
            ui.text_l(f'Hello {q.user.player.first.title()},'),
            ui.text_xs('⠀'),
            ui.text_m('Do you want to play a guessing game?'),
            ui.text_xs('⠀'),
            ui.buttons(
                items=[
                    ui.button('start_game', label='Play', primary=True),
                    ui.button('leaderboard', label='View Scores', primary=False),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def show_leaderboard(q: Q):
    columns = [
        ui.table_column(
            name='name',
            label='Name',
            sortable=True,
            searchable=False,
            max_width='230',
            data_type='string',
            link=False,
        ),
        ui.table_column(
            name='number',
            label='Number',
            sortable=True,
            max_width='100',
            data_type='number',
        ),
        ui.table_column(
            name='num_of_guesses',
            label='# of Guesses',
            sortable=True,
            max_width='120',
            data_type='number',
        ),
        ui.table_column(
            name='game_time',
            label='Time (s)',
            sortable=True,
            max_width='160',
            data_type='number',
        ),
    ]
    scores = [
        ui.table_row(
            name=game.game_id,
            cells=[
                q.app.players[game.player_id].name,
                str(game.number),
                str(len(game.guesses)),
                str(game.time_seconds()),
            ],
        )
        for game in q.app.games.values()
    ]
    leaderboard = ui.table(
        name='leaderboard',
        columns=columns,
        rows=scores,
        groupable=False,
        downloadable=False,
        resettable=False,
        height='600px',
    )
    del q.page['starting_game']
    q.page['leaderboard'] = ui.form_card(
        box='3 2 5 9',
        items=[
            ui.label('Scores'),
            leaderboard,
            ui.text_xs('⠀'),
            ui.buttons(
                items=[
                    ui.button(name='start_game', label='Play', primary=True),
                    ui.button(name='leaderboard', label='Refresh', primary=True),
                    ui.button(
                        name='private_leaderboard',
                        label='Show my games only',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def show_private_leaderboard(q: Q):
    columns = [
        ui.table_column(
            name='game_id',
            label='Game #',
            sortable=False,
            searchable=False,
            max_width='150',
            data_type='string',
            link=False,
        ),
        ui.table_column(
            name='number',
            label='Number',
            sortable=True,
            max_width='90',
            data_type='number',
        ),
        ui.table_column(
            name='num_of_guesses',
            label='# of Guesses',
            sortable=True,
            max_width='120',
            data_type='number',
        ),
        ui.table_column(
            name='status',
            label='Status',
            sortable=False,
            filterable=True,
            max_width='90',
            data_type='string',
            cell_type=ui.icon_table_cell_type(),
        ),
        ui.table_column(
            name='game_time',
            label='Time (s)',
            sortable=True,
            max_width='150',
            data_type='number',
        ),
    ]
    scores = [
        ui.table_row(
            name=game.game_id,
            cells=[
                str(idx),
                str(game.number),
                str(len(game.guesses)),
                'MedalSolid' if game.status == 'done' else 'Running',
                str(game.time_seconds()),
            ],
        )
        for idx, game in enumerate(q.user.player.games.values(), 1)
    ]
    leaderboard = ui.table(
        name='leaderboard',
        columns=columns,
        rows=scores,
        groupable=False,
        downloadable=False,
        resettable=False,
        height='600px',
    )
    del q.page['starting_game']
    q.page['leaderboard'] = ui.form_card(
        box='3 2 5 9',
        items=[
            ui.label('Scores from your games'),
            leaderboard,
            ui.text_xs('⠀'),
            ui.buttons(
                items=[
                    ui.button(name='start_game', label='Play', primary=True),
                    ui.button(name='leaderboard', label='Show all games', primary=True),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


def app_initialize(q: Q):
    if not q.app.initialized:
        q.app.games = {}
        q.app.players = {}
        q.app.initialized = True


def user_initialize(q: Q):
    player_id = q.auth.subject
    if player_id not in q.app.players:
        q.user.player = Player(email=q.auth.username, player_id=player_id)
        q.app.players[player_id] = q.user.player


async def client_initialize(q: Q):
    if not q.client.initialized:
        await make_base_ui(q)
        await make_welcome_card(q)
        q.client.initialized = True


async def theme_switch_handler(q: Q):

    q.client.active_theme = 'h2o-dark' if q.args.toggle_theme else 'default'
    q.page['meta'].theme = q.client.active_theme
    q.page['title'].items[0].toggle.value = q.client.active_theme == 'h2o-dark'
    await q.page.save()


async def run_app(q: Q):
    if q.args.start_game:
        if q.args.submit_game:
            q.client.game.is_public = True
            q.app.games[q.client.game.game_id] = q.client.game
        del q.page['leaderboard']
        del q.page['hello']
        await start_new_game(q)
    elif q.args.quit_game:
        del q.page['starting_game']
        await make_welcome_card(q)
    elif q.args.guess:
        message = q.client.game.guess(q.args.guess)
        if message == 'You Got It!':
            q.page['starting_game'].items = [
                ui.text_l(
                    f'🏅 🎉 🎂 You Got It, The number is **{q.client.game.number}**'
                ),
                ui.text_m(
                    f'You made **{len(q.client.game.guesses)}** guesses in'
                ),
                ui.text_m(f'{q.client.game.game_time()}.'),
                ui.toggle(
                    name='submit_game',
                    label='Submit your game to Public Scoreboard',
                    trigger=False,
                ),
                ui.text_xs('⠀'),
                ui.buttons(
                    items=[
                        ui.button(
                            name='leaderboard',
                            label='View Scores',
                            primary=True,
                        ),
                        ui.button(
                            name='start_game',
                            label='Play Again',
                            primary=False,
                        ),
                    ],
                    justify='center',
                ),
            ]
        else:
            previous_guesses = [str(x) for x in q.client.game.guesses]
            if len(previous_guesses) > 16:
                previous_guesses = previous_guesses[-16:]
                previous_guesses[0] = '...'
            guesses_str = ", ".join(previous_guesses)
            q.page['starting_game'].items = [
                ui.text_l(message),
                ui.text_m(guesses_str),
                ui.text_xs('⠀'),
                ui.slider(
                    name='guess',
                    label='your guess',
                    min=1,
                    max=100,
                    value=q.args.guess,
                    trigger=True,
                ),
                ui.text_xs('⠀'),
                ui.buttons(
                    items=[ui.button(name='quit_game', label='Quit', primary=True)],
                    justify='center',
                ),
            ]
    elif q.args.leaderboard:
        if q.args.submit_game:
            q.client.game.is_public = True
            q.app.games[q.client.game.game_id] = q.client.game
        del q.page['starting_game']
        await show_leaderboard(q)
    elif q.args.private_leaderboard:
        await show_private_leaderboard(q)

    if q.args.toggle_theme is not None:
        await theme_switch_handler(q)
    await q.page.save()


@app('/')
async def serve(q: Q):
    print(q.args)
    app_initialize(q)
    user_initialize(q)
    await client_initialize(q)
    await run_app(q)
