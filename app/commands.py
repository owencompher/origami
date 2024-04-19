import os
from models import Poll, Option, Vote, User
from pprint import pp
from app import now


def get_user_or_none(interaction):
    return User.get_or_none(duid=interaction['user']['id'])


def start(interaction):
    os.system('sendmc start')
    return {"type": 4, "data": {"content": "sent start command to the minecraft server"}}


def poll(interaction):
    user = get_user_or_none(interaction)

    response = {"type": 4, "data": {"content": "to be implemented"}}
    if interaction["data"]["options"][0]["name"] == 'list':
        pass  # make and return list

    elif interaction["data"]["options"][0]["name"] == 'get':
        id = interaction["data"]["options"][0]["options"][0]["value"]
        poll = Poll.get_or_none(Poll.id == id)
        poll.options = [option for option in poll.options]
        poll.flags = poll.flags()
        poll.description = poll.description + "\n\n" if poll.description else ""

        # todo:
        # - restrict polls based on open/closed status
        # - get user votes to set as defaults
        # - interaction handler to update votes

        open = True
        poll.status = ""
        if now() < poll.opens:
            timestamp = int(poll.opens.timestamp())
            open = False
            poll.status = f"opens <t:{timestamp}:f> (<t:{timestamp}:R>)"
        elif poll.closes:
            timestamp = int(poll.closes.timestamp())
            if now() < poll.closes: poll.status = f"closes <t:{timestamp}:f> (<t:{timestamp}:R>)"
            else:
                open = False
                poll.status = f"closed <t:{timestamp}:f> (<t:{timestamp}:R>)"

        votes = []
        if user:
            options = Option.select(Option.id).where(Option.poll == poll)
            votes = Vote.select(Vote).where((Vote.option.in_(options)) & (Vote.user == user))
            votes = [vote.option.id for vote in votes]

        response = {
            "type": 4,
            "data": {
                "content": f"## {poll.name}\n"
                           f"poll {poll.id} {poll.status}\n"
                           f"\n{poll.description}"
                           f"your vote:",
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 3,
                                "custom_id": "vote",
                                #"disabled": not open,
                                "options": [
                                    {
                                        "label": f"{option.name}",
                                        "value": f"{str(poll.id)} {str(option.id)}",
                                        "description": option.description,
                                        "default": option.id in votes,
                                    }
                                    for option in poll.options
                                ],
                                "min_values": 1 if poll.flags['single'] else 0,
                                "max_values": 1 if poll.flags['single'] else len(poll.options),
                            }
                        ]
                    }
                ]
            }
        }
    pp(response)
    return response


def vote(interaction):

    # todo: figure out how to get poll_id into vote data when votes(values) empty
    return {"type": 4, "data": {"content": "to be implemented"}}



    pollid = int(interaction['data']['values'][0].split()[0])
    votes = [int(val.split()[1]) for val in interaction['data']['values']]

    user = get_user_or_none(interaction)
    if not user: return {"type": 4, "data": {"content": "you are not associated with a user in origami"}}

    poll = Poll.get_or_none(Poll.id == pollid)
    if not poll: return {"type": 4, "data": {"content": "problem voting in this poll"}}

    poll.options = [option for option in poll.options]
    poll.flags = poll.flags()
    if now() < poll.opens or (poll.closes and now() > poll.closes): return {"type": 4, "data": {"content": "the poll is closed"}}

    for vote in votes:
            if not Option.get_or_none(vote): return {"type": 4, "data": {"content": "something you voted for doesn't exist"}}
    options = Option.select(Option.id).where(Option.poll == poll)
    Vote.delete().where((Vote.option.in_(options)) & (Vote.user == user)).execute()

    for vote in votes:
            Vote.create(user=user, option=vote)

    for op in options:
        option = Option.get_by_id(op)
        option.count = option.count_votes()
        print(option)
        option.save()

    response = {"type": 4, "data": {"content": f"updated vote on poll {interaction['data']['values'][0].split()[0]}"}}
    return response


commands = {
    "polls": poll,
    "vote": vote,
    "start": start
}
