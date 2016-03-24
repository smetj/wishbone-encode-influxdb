#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  influxdb.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone import Actor
from wishbone.event import Metric


class InfluxDB(Actor):

    '''**Converts the internal metric format to InfluxDB line format.**

    Incoming date must be of type <Metric>.


    Parameters:

        - script(bool)(True)
           |  Include the script name.

        - pid(bool)(False)
           |  Include pid value in script name.

        - source(bool)(True):
           |  Include the source name in the naming schema.


    Queues:

        - inbox
           |  Incoming messages

        - outbox
           |  Outgoing messges
    '''

    def __init__(self, actor_config):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.pool.createQueue("outbox")
        self.registerConsumer(self.consume, "inbox")
        self.tags = {}

    def consume(self, event):

        data = event.get()

        if isinstance(data, Metric):
            event.set(self.generate(data))
            self.submit(event, self.pool.queue.outbox)
        else:
            self.logging.error("Event dropped because not of type <wishbone.event.Metric>")

    def generate(self, data):

        name = data.name.split('.')
        return "{name},source={source},type={type},module={module},queue={queue} value={value:.5f} {time:20.0f}".format(
                    name=name[4],
                    source=data.source,
                    type=data.type,
                    module=name[1],
                    queue=name[3],
                    value=data.value,
                    time=data.time * 1000000000)
