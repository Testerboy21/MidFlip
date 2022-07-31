supported_games = ['Crash', 'Towers']

supported_games_to_string= ", ".join(str(x) for x in supported_games)

print("Please select one of the support games: ", supported_games_to_string)

user_input = input()

for x in range(len(supported_games)):
    supported_games[x] = supported_games[x].lower()

if user_input.lower() in supported_games:
    exec(open(user_input.lower() + ".py").read())
else:
    print("Valid game not entered!")