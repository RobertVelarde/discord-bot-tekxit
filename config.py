# Server status 'enum'
starting = 0
running  = 1
stopping = 2
stopped  = 3

regexDone = '\[\d{2}:\d{2}:\d{2}\] \[Server thread\/INFO] \[minecraft\/DedicatedServer]: Done'
regexFml = 'Run the command /fml confirm or or /fml cancel to proceed.'
regexJoin = '^\[\d{2}:\d{2}:\d{2}\] \[Server thread\/INFO] \[minecraft\/PlayerList]: .*\[\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}\] logged in with entity id'
regexLeave = '^\[\d{2}:\d{2}:\d{2}\] \[Server thread\/INFO] \[minecraft\/NetHandlerPlayServer]: .* lost connection:'
regexLine = '\n'

discordToken = ""
