import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import randint
from typing import Dict, List

from h2o_wave import Q, app, main, ui


@dataclass
class WaveColors:
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
        if self.status != 'playing':
            return 'Game already finished!'
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
        time_str = f'**{seconds}** Seconds, and **{duration.microseconds}** Microseconds'
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
    # Clear any previous game state
    q.client.game = None
    q.client.completed_game_for_submission = None

    q.client.game = Game(q.user.player.player_id)
    q.user.player.games[q.client.game.game_id] = q.client.game

    q.page['starting_game'] = ui.form_card(
        box='4 4 3 3',
        items=[
            ui.text_l('I am thinking of a number between 1 and 100'),
            ui.text_m('Can you guess what it is?'),
            ui.text_xs('⠀'),
            ui.slider(
                name='guess',
                label='Your guess',
                min=1,
                max=100,
                value=50,
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
        box='1 1 -1 1',
        title='Guess the Number',
        subtitle=f'Player: {q.user.player.name}',
        icon='ChatBot',
        icon_color=WaveColors.cyan,
        color='card',
        items=[
            ui.toggle(name='toggle_theme', label='Dark theme', trigger=True),
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
    # Only include completed public games
    public_games = [g for g in q.app.games.values() if g.status == 'done' and g.is_public]

    columns = [
        ui.table_column(name='name', label='Name', max_width='200'),
        ui.table_column(name='number', label='Number', data_type='number', max_width='80'),
        ui.table_column(name='num_of_guesses', label='# Guesses', data_type='number', max_width='100'),
        ui.table_column(name='game_time', label='Time (s)', data_type='number', max_width='100'),
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
        for game in public_games
    ]
    q.page['leaderboard'] = ui.form_card(
        box='3 2 5 9',
        items=[
            ui.label('Public Leaderboard'),
            ui.table(
                name='leaderboard_table',
                columns=columns,
                rows=scores,
                height='500px'
            ),
            ui.text_xs('⠀'),
            ui.buttons(
                items=[
                    ui.button(name='start_game', label='Play', primary=True),
                    ui.button(name='private_leaderboard', label='My Games', primary=False),
                ],
                justify='center',
            ),
        ],
    )
    # Clean up other cards
    for card in ['hello', 'starting_game']:
        if card in q.page:
            del q.page[card]
    await q.page.save()


async def show_private_leaderboard(q: Q):
    player_games = [g for g in q.user.player.games.values() if g.status == 'done']

    columns = [
        ui.table_column(name='idx', label='Game #', max_width='80'),
        ui.table_column(name='number', label='Number', data_type='number', max_width='80'),
        ui.table_column(name='guesses', label='# Guesses', data_type='number', max_width='100'),
        ui.table_column(name='time', label='Time (s)', data_type='number', max_width='100'),
        ui.table_column(name='public', label='Public', max_width='80'),
    ]
    scores = [
        ui.table_row(
            name=game.game_id,
            cells=[
                str(i + 1),
                str(game.number),
                str(len(game.guesses)),
                str(game.time_seconds()),
                '✅' if game.is_public else '🔒',
            ],
        )
        for i, game in enumerate(player_games)
    ]
    q.page['leaderboard'] = ui.form_card(
        box='3 2 5 9',
        items=[
            ui.label('Your Completed Games'),
            ui.table(name='private_table', columns=columns, rows=scores, height='500px'),
            ui.text_xs('⠀'),
            ui.buttons(
                items=[
                    ui.button(name='start_game', label='Play', primary=True),
                    ui.button(name='leaderboard', label='Public Scores', primary=False),
                ],
                justify='center',
            ),
        ],
    )
    for card in ['hello', 'starting_game']:
        if card in q.page:
            del q.page[card]
    await q.page.save()


def app_initialize(q: Q):
    if not q.app.initialized:
        q.app.games = {}
        q.app.players = {}
        q.app.initialized = True


def user_initialize(q: Q):
    player_id = q.auth.subject or 'anonymous'
    if player_id not in q.app.players:
        q.user.player = Player(email=q.auth.username or 'guest@example.com', player_id=player_id)
        q.app.players[player_id] = q.user.player
    else:
        q.user.player = q.app.players[player_id]


async def client_initialize(q: Q):
    if not q.client.initialized:
        await make_base_ui(q)
        await make_welcome_card(q)
        q.client.initialized = True
        q.client.active_theme = 'default'


async def theme_switch_handler(q: Q):
    q.client.active_theme = 'h2o-dark' if q.args.toggle_theme else 'default'
    q.page['meta'].theme = q.client.active_theme
    await q.page.save()


async def run_app(q: Q):
    # Handle theme
    if q.args.toggle_theme is not None:
        await theme_switch_handler(q)
        return

    # Start new game
    if q.args.start_game:
        for card in ['hello', 'leaderboard']:
            if card in q.page:
                del q.page[card]
        await start_new_game(q)
        return

    # Quit game
    if q.args.quit_game:
        del q.page['starting_game']
        await make_welcome_card(q)
        return

    # Make a guess
    if q.args.guess is not None and q.client.game:
        message = q.client.game.guess(int(q.args.guess))
        if message == 'You Got It!':
            # Store completed game for potential submission
            q.client.completed_game = q.client.game
            q.page['starting_game'].items = [
                ui.text_l(f'🏅 🎉 You Got It! The number was **{q.client.game.number}**'),
                ui.text_m(f'You made **{len(q.client.game.guesses)}** guesses in'),
                ui.text_m(f'{q.client.game.game_time()}.'),
                ui.toggle(
                    name='submit_game',
                    label='Submit to Public Leaderboard',
                    value=False,
                    trigger=False,
                ),
                ui.text_xs('⠀'),
                ui.buttons(
                    items=[
                        ui.button(name='leaderboard', label='View Scores', primary=True),
                        ui.button(name='start_game', label='Play Again', primary=False),
                    ],
                    justify='center',
                ),
            ]
        else:
            guesses_str = ", ".join(str(g) for g in q.client.game.guesses[-10:])  # last 10
            if len(q.client.game.guesses) > 10:
                guesses_str = "…, " + guesses_str
            q.page['starting_game'].items = [
                ui.text_l(message),
                ui.text_m(f'Your guesses: {guesses_str}'),
                ui.text_xs('⠀'),
                ui.slider(
                    name='guess',
                    label='Your guess',
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
        await q.page.save()
        return

    # View leaderboards
    if q.args.leaderboard:
        # Handle submission BEFORE showing leaderboard
        if q.args.submit_game and hasattr(q.client, 'completed_game'):
            q.client.completed_game.is_public = True
            q.app.games[q.client.completed_game.game_id] = q.client.completed_game
            delattr(q.client, 'completed_game')  # prevent re-submission
        await show_leaderboard(q)
        return

    if q.args.private_leaderboard:
        await show_private_leaderboard(q)
        return

    await q.page.save()


@app('/')
async def serve(q: Q):
    app_initialize(q)
    user_initialize(q)
    await client_initialize(q)
    await run_app(q)