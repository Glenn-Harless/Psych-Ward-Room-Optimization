"""
This file represents the current model.

The Current Model being:

- All rooms are Double Rooms (2 beds per room)
- 26 total beds (13 double rooms)

When a patient has extra needs and cannot be safely kept with other people, the second bed becomes unavailable/held
- This is a wasted bed.

We want to look historically at all the data and do the following:

- Calculate wasted beds for each day given the room configuration

"""