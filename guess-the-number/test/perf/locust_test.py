from locust import HttpUser, TaskSet, task, tag, between, SequentialTaskSet
import os
import random

'''
Please export below env variables prior to run the Wave application.
export H2O_WAVE_APP_ACCESS_KEY_ID=admin
export H2O_WAVE_APP_ACCESS_KEY_SECRET=test123
'''

key_id = os.environ['H2O_WAVE_APP_ACCESS_KEY_ID']
secret = os.environ['H2O_WAVE_APP_ACCESS_KEY_SECRET']

# validate response of the HTTP request
def validate_response(client, response, response_threshold=5):
    response_time = response.elapsed.total_seconds()  # time that spent to receive response for a sent http request.

    # response code that received for a sent http request. Status code 200 means a successful one.
    response_code = response.status_code

    if response_code != 200:  # If response code is not 200, then test case marked as a filed one.
        response.failure(
            "Test [%s], unsuccessful response code [%d]" % (client.user.fullname(), response_code))
    # if a response take more than the threshold time, the testcase marked as a filed one.
    elif (response_time > response_threshold):
        response.failure("Test [%s], request took too long (%d), threshold %d" %
                         (client.user.fullname(), response_time, response_threshold))
    else:
        response.success()  # marked response as a success one.


class PlayTest(SequentialTaskSet):

    # click play
    @tag('GuessTheNumber', 'perf')
    @task
    def click_play(self):
        with self.client.post("/", name="click play", auth=(key_id, secret),
                              json={"start_game": "true", "leaderboard": "false"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)

    # click your guess
    @tag('GuessTheNumber', 'perf')
    @task
    def click_guess(self):
        with self.client.post("/", name="click your guess", auth=(key_id, secret),
                              json={"guess": random.randint(1, 100), "quit_game": "false"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)

    # click quit
    @tag('GuessTheNumber', 'perf')
    @task
    def click_quit(self):
        with self.client.post("/", name="click quit", auth=(key_id, secret),
                              json={"quit_game": "true"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)


class ViewScoreTest(TaskSet):
    # click view score
    @tag('GuessTheNumber', 'perf')
    @task(2)
    def click_view_score(self):
        with self.client.post("/", name="click view score", auth=(key_id, secret),
                              json={"start_game": "false", "leaderboard": "true"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)

    # click refresh
    @tag('GuessTheNumber', 'perf')
    @task(1)
    def click_refresh(self):
        with self.client.post("/", name="click refreshr", auth=(key_id, secret),
                              json={"leaderboard": "true", "start_game": "false", "private_leaderboard": "false"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)

    # click show all games
    @tag('GuessTheNumber', 'perf')
    @task(1)
    def click_show_all_games(self):
        with self.client.post("/", name="click show all games", auth=(key_id, secret),
                              json={"leaderboard": "false", "start_game": "false", "private_leaderboard": "true"},
                              catch_response=True) as response:
            validate_response(self.client, response, 5)


class User(HttpUser):
    tasks = [PlayTest, ViewScoreTest]
    # User will do operations within 1-5 seconds
    wait_time = between(1, 5)
