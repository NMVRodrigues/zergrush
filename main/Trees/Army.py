import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer

import BehaviourTree
from BehaviourTree import *
import Trees.Defense as defense

hasAttacked = False


# instance represents the bot itself, so we can tell it to do stuff
class Action:
    """A way of passing the variables"""

    def __init__(self, inst):
        self.instance = inst
        self.warpgate_started = False

    async def trainZealots(self):
        if not self.instance.can_afford(UnitTypeId.ZEALOT):
            return False
        for gate in self.instance.units(UnitTypeId.GATEWAY).ready:
            if gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.ZEALOT))
                return True
        return False

    async def shouldTrainZealots(self):
        if len(self.instance.units(UnitTypeId.ZEALOT)) < 4 and not self.instance.already_pending(UnitTypeId.ZEALOT):
            return True
        # TODO: check for cybernetics core and gateways, then train 3 more
        # if self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
        if len(self.instance.units(UnitTypeId.ZEALOT)) < 7 and not self.instance.already_pending(UnitTypeId.ZEALOT):
            return True
        return False

    async def haveGateway(self):
        return self.instance.units(UnitTypeId.GATEWAY).ready.amount > 0

    async def haveStarGate(self):
        return self.instance.units(UnitTypeId.STARGATE).ready.amount > 0

    async def shouldTrainStalkers(self):
        if self.instance.units(UnitTypeId.STALKER).ready.amount < 13:
            return True
        # TODO: check for cybernetics core and gateways, then train 3 more
        # if self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists:
        return False

    async def buildCyberneticsCore(self):
        if self.instance.can_afford(UnitTypeId.CYBERNETICSCORE):
            nexus = self.instance.units(UnitTypeId.NEXUS).ready.random
            await self.instance.build(UnitTypeId.CYBERNETICSCORE,
                                      near=nexus.position.towards(self.instance.game_info.map_center, distance=10))
            return True
        return False

    async def shouldBuildCyberneticsCore(self):
        if not self.instance.units(UnitTypeId.CYBERNETICSCORE).exists and not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE):
            return len(self.instance.units(UnitTypeId.ZEALOT)) >= 3
        return False

    async def arleadyHaveCyberCore(self):
        return self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.exists and \
               not self.instance.already_pending(UnitTypeId.CYBERNETICSCORE)

    async def arleadyHaveAllGates(self):
        return self.instance.units(UnitTypeId.GATEWAY).ready.amount >= 3

    async def arleadyHaveEnoughStarGate(self):
        return self.instance.units(UnitTypeId.STARGATE).amount > 3

    async def doWarpGateResearch(self):
        #abilities = await self.get_available_abilities(ccore)
        if not self.instance.can_afford(AbilityId.RESEARCH_WARPGATE) and self.instance.warpgate_started:
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(UnitTypeId.RESEARCH_WARPGATE))
        self.warpgate_started = True
        return True

    async def researchAirAmor(self):
        #abilities = await self.get_available_abilities(ccore)
        print("Research started!!!!!!!!!")
        if not self.instance.can_afford(AbilityId.RESEARCH_PROTOSSAIRARMOR):
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(AbilityId.RESEARCH_PROTOSSAIRARMOR))
        return True

    async def researchAirWeapon(self):
        #abilities = await self.get_available_abilities(ccore)
        if not self.instance.can_afford(AbilityId.RESEARCH_PROTOSSAIRWEAPONS):
            return False
        ccore = self.instance.units(UnitTypeId.CYBERNETICSCORE).ready.first
        await self.instance.do(ccore(AbilityId.RESEARCH_PROTOSSAIRWEAPONS))
        return True

    async def haveResourcesForStalker(self):
        return self.instance.can_afford(UnitTypeId.STALKER)

    async def haveEnoughStalkers(self):
        return self.instance.units(UnitTypeId.STALKER).amount >= 10

    async def haveEnoughZealots(self):
        return self.instance.units(UnitTypeId.ZEALOT).ready.amount > 4

    async def trainStalkers(self):
        print("Train Stalkers")
        for gate in self.instance.units(UnitTypeId.GATEWAY):
            if self.instance.can_afford(UnitTypeId.STALKER) and gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.STALKER))
                return True
        return False

    async def trainVR(self):
        for gate in self.instance.units(UnitTypeId.STARGATE):
            if self.instance.can_afford(UnitTypeId.VOIDRAY) and gate.noqueue:
                await self.instance.do(gate.train(UnitTypeId.VOIDRAY))
                return True
        return False

    async def hasAttackedBase(self):
        # print("Has Attacked Base ", hasAttacked, "-----")
        return hasAttacked

    async def rushEnemyBaseWithEverything(self):
        global hasAttacked
        hasAttacked = True
        attackLocation = None
        if len(self.instance.enemy_start_locations) > 0:
            attackLocation = self.instance.enemy_start_locations[0]
        elif self.instance.known_enemy_structures.exists:
            attackLocation = random.choice(self.instance.known_enemy_structures)
        else:
            return False

        for stalker in self.instance.units(UnitTypeId.STALKER):
            await self.instance.do(stalker.attack(attackLocation))
        for zealot in self.instance.units(UnitTypeId.ZEALOT):
            await self.instance.do(zealot.attack(attackLocation))
        for vr in self.instance.units(UnitTypeId.VOIDRAY):
            await self.instance.do(vr.attack(attackLocation))
        for vr in self.instance.units(UnitTypeId.OBSERVER):
            await self.instance.do(vr.attack(attackLocation))
        return True

    async def doNothing(self):
        return True

    async def applyDefenseTree(self):
        defense.defAction(self.instance)
        await defense.runTree()

    async def shouldTrainObserver(self):
        return self.instance.units(UnitTypeId.ROBOTICSFACILITY).ready.exists and\
            not self.instance.already_pending(UnitTypeId.OBSERVER) and\
            not self.instance.units(UnitTypeId.OBSERVER).ready.exists

    async def canTrainObserver(self):
        return self.instance.can_afford(UnitTypeId.OBSERVER)

    async def trainObserver(self):
        robotics = self.instance.units(UnitTypeId.ROBOTICSFACILITY).ready
        if robotics.exists:
            await self.instance.do(robotics.first.train(UnitTypeId.OBSERVER))
            return True
        return False


action = Action(None)


def defAction(instance):
    global action
    action.instance = instance


#hasMinimumTroops
s3 = Sequence(
    Atomic(action.arleadyHaveAllGates),
    Atomic(action.haveEnoughZealots), #do we have enough zealots?
    Atomic(action.haveEnoughStalkers), #do we have enough stalkers?
    #ConditionalElse(action.hasAttackedBase,
    #    DoAllSequence(
    #        OptionalConditional(action.arleadyHaveEnoughStarGate,
    #            Atomic(action.trainVR),
    #        ),
    #        ConditionalElse(action.haveEnoughZealots,
    #            Atomic(action.doNothing),
    #            Atomic(action.trainZealots)
    #        ),
    #        ConditionalElse(action.haveEnoughStalkers,
    #            Atomic(action.doNothing),
    #            Atomic(action.trainStalkers)
    #        )
    #    ),
    #    Atomic(action.rushEnemyBaseWithEverything)
    #)
    Atomic(action.rushEnemyBaseWithEverything)
)


#TREE
s2 = DoAllSequence(
    Atomic(s3.run),
    Sequence(
        Atomic(action.haveGateway),#check if we have a gateway
        OptionalConditional(action.shouldTrainZealots,
            Atomic(action.trainZealots)
        ),
        OptionalConditional(action.shouldTrainStalkers,
            Conditional(action.haveResourcesForStalker,
                Atomic(action.trainStalkers), #Train stalkers
            )
        )
    ),
    Sequence(
        Atomic(action.haveStarGate),
        Atomic(action.trainVR)
    ),
    Sequence(
        Atomic(action.shouldTrainObserver),
        Conditional(action.canTrainObserver,
            Atomic(action.trainObserver),
        ),
    ),
    #Conditional(action.arleadyHaveCyberCore, #Do we arleady have one?
    #   Selector(
    #       Conditional(action.arleadyHaveAllGates,
    #            Selector(
    #                Atomic(s3.run),
    #                ConditionalElse(action.haveResourcesForStalker,
    #                    Atomic(action.trainStalkers), #Train stalkers
    #                    Atomic(action.doNothing) #Save resources for later
    #                )
    #            )
    #        ),
#
#            #Atomic(action.researchAirAmor),
#            #Atomic(action.researchAirWeapon)
#            #Atomic(action.doWarpGateResearch)
#        ) #Build more gateways
#    ),
#    Conditional(action.shouldTrainZealots,
#                Atomic(action.trainZealots)),
)

s1 = DoAllSequence(
    Selector(
        #Atomic(s3.run),
        #Atomic(action.applyDefenseTree)
        ConditionalElse(action.haveEnoughStalkers, #do we have to attack? TODO -> needs to be swithced with something a bit more complex
            Sequence(
                OptionalConditional(action.shouldTrainObserver,
                    OptionalConditional(action.canTrainObserver,
                        Atomic(action.trainObserver),
                    ),
                ),
                Atomic(action.rushEnemyBaseWithEverything), # TODO -> change for the attacker version MAYBE THE CONDITION AND THE ATTACK TREE SHOULD BE IN THE SAME PLACE
            ),
            Atomic(action.applyDefenseTree),
        ),
    ),
    Atomic(s2.run),
)


async def runTree():
    global action
    if action is not None:
        await s1.run()
    else:
        return False
    return True
