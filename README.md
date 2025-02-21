# mc-shell

A simple IPython shell using magic functions and tab completion.

## Setup and Configuration ##

### Clone it ###
```commandline
git clone https://github.com/d4g33z/mc-shell.git
```
### Install into a Virtual Environment
```commandline
# cd mc-shell
# python3 -m venv --clear --prompt mcshell env
# . env/bin/activate
# pip install .
```

## Usage ##

```commandline
# mcshell start
[ins] In [1]: %mc_help
advancement (grant|revoke)
attribute <target> <attribute> (base|get|modifier)
ban <targets> [<reason>]
ban_ip <target> [<reason>]
banlist 
bossbar (add|get|list|remove|set)
clear [<targets>]
clone <begin> <end> <destination> 
data (get|merge|modify|remove)
datapack (disable|enable|list)
debug (report|start|stop)
defaultgamemode (adventure|creative|spectator|survival)
deop <targets>
difficulty 
effect (clear|give)
enchant <targets> <enchantment> [<level>]
execute (align|anchored|as|at|facing|if|in|positioned|rotated|run|store|unless)
experience (add|query|set)
fill <from> <to> <block> 
forceload (add|query|remove)
function <name>
gamemode (adventure|creative|spectator|survival)
gamerule 
(announceAdvancements|commandBlockOutput|disableElytraMovementCheck|disableRaids|doDaylightCycle|doEntityDrops|doFireTick|doImmediateRespawn|doIn
somnia|doLimitedCrafting|doMobLoot|doMobSpawning|doPatrolSpawning|doTileDrops|doTraderSpawning|doWeatherCycle|drowningDamage|fallDamage|fireDamag
e|forgiveDeadPlayers|keepInventory|logAdminCommands|maxCommandChainLength|maxEntityCramming|mobGriefing|naturalRegeneration|randomTickSpeed|reduc
edDebugInfo|sendCommandFeedback|showDeathMessages|spawnRadius|spectatorsGenerateChunks|universalAnger)
give <targets> <item> [<count>]
help [<command>]
kick <targets> [<reason>]
kill [<targets>]
list 
locate 
(bastion_remnant|buried_treasure|desert_pyramid|endcity|fortress|igloo|jungle_pyramid|mansion|mineshaft|monument|nether_fossil|ocean_ruin|pillage
r_outpost|ruined_portal|shipwreck|stronghold|swamp_hut|village)
locatebiome <biome>
loot (give|insert|replace|spawn)
me <action>
msg <targets> <message>
op <targets>
pardon <targets>
pardon_ip <target>
particle <name> [<pos>]
playsound <sound> (ambient|block|hostile|master|music|neutral|player|record|voice|weather)
recipe (give|take)
reload
replaceitem (block|entity)
save_all 
save_off
save_on
say <message>
schedule (clear|function)
scoreboard (objectives|players)
seed
setblock <pos> <block> 
setidletimeout <minutes>
setworldspawn [<pos>]
spawnpoint [<targets>]
spectate [<target>]
spreadplayers <center> <spreadDistance> <maxRange> (under|<respectTeams>)
stop
stopsound <targets> [*|ambient|block|hostile|master|music|neutral|player|record|voice|weather]
summon <entity> [<pos>]
tag <targets> (add|list|remove)
team (add|empty|join|leave|list|modify|remove)
teammsg <message>
teleport (<destination>|<location>|<targets>)
tell -> msg
tellraw <targets> <message>
time (add|query|set)
title <targets> (actionbar|clear|reset|subtitle|times|title)
tm -> teammsg
tp -> teleport
trigger <objective> 
w -> msg
weather (clear|rain|thunder)
whitelist (add|list|off|on|reload|remove)
worldborder (add|center|damage|get|set|warning)
xp -> experience
```
```commandline
[ins] In [2]: %mc_help <TAB>
ban             clear           debug           effect          fill            gamerule         
ban_ip          clone           defaultgamemode enchant         forceload       give             
advancement     banlist         data            deop            execute         function        help            >
attribute       bossbar         datapack        difficulty      experience      gamemode        kick  
[ins] In [3]: %mc_help advancement
Gives, removes, or checks player advancements.
https://minecraft.fandom.com/wiki/Commands/advancement

advancement (grant|revoke) <targets> everything
advancement (grant|revoke) <targets> only <advancement> [<criterion>]
advancement (grant|revoke) <targets> from <advancement>
advancement (grant|revoke) <targets> through <advancement>
advancement (grant|revoke) <targets> until <advancement>
```

```commandline
[ins] In [3]: %mc_run weather
Send: weather
Response:
----------------------------------------------------------------------------------------------------
Error in usage:
Sets the weather.
https://minecraft.fandom.com/wiki/Commands/weather

weather (clear|rain|thunder) [<duration>]
----------------------------------------------------------------------------------------------------
```

```commandline
[ins] In [4]: %mc_run weather <TAB>
clear  
rain   
thunder
```

```commandline
[ins] In [5]: %mc_run weather clear
Send: weather clear
Response:
----------------------------------------------------------------------------------------------------
Set the weather to clear
----------------------------------------------------------------------------------------------------
```
