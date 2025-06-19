# MegaManZeroQoLPatcher

### Mega Man Zero Series Quality of Life Patcher
* A tool to modify the Mega Man Zero games with various Quality of Life (QoL) tweaks such as reducing weapon requirements or making EX skills not require A rank or higher

### Setup to get this tool working
* Have one of the following ROMs
  * Megaman Zero (USA, Europe) (md5 of **b24a17d080a01a404cbf018ba42b9803**)
  * Megaman Zero 2 (USA) (md5 of **182363b0698322e1864ced6e9eed7ead**)
  * Megaman Zero 3 (USA) (md5 of **aa1d5eeffcd5e4577db9ee6d9b1100f9**)
  * Megaman Zero 4 (USA) (md5 of **0d1e88bdb09ff68adf9877a121325f9c**)
* Navigate to the game you'd like to patch and select the ROM
* Please be patient when your ROM is being patched. It'll look like nothing is happening, but wait for the confirmation that it's done
* Have fun playing the Mega Man Zero games with some QoL tweaks!

### What QoL tweaks does this tool have?
* 9 Retry Chips at Start of Game (Zero 1 only)
* Battle Network Viruses Without Game Link (Zero 3 only) (more of an easter egg than anything)
* Blood Restoration (all games)
* Get EX Skill Regardless of Rank (Zero 2 and 3)
* Japanese Vocal Restoration (Zero 4 only)
* Modify Cyber-Elf/Croire Costs (all games)
* Modify Weapon EXP (Zero 1 and 2)
* Remove Cyber-Elf Penalty on Rank (Zero 1 and 2)

### Why no Europe or Japanese ROM support?
* This is a question I might get if someone uses this. The answer is that this is for multiple reasons
  * While Europe and USA Zero 2 is mostly identical and would work with this patcher, Zero 3 and 4 are not and would break the ROM if it's not USA. The patches and hex offsets this tool uses are based on the USA ROM and are vastly different since the Zero 3 and 4 ROMs are very different internally
  * Japanese ROM support would be pointless to me and this tools use since everything I and most people would want that was removed from the international versions can be patched back in
* While I could add support for these in the future, it's not a goal of this project

### Credits
* Credit to acediez for their EX skill patches for Zero 2 and 3
  * Patches Link: https://www.romhacking.net/forum/index.php?topic=27346.0
* Credit to acediez for their Battle Network Virus patch for Zero 3
  * Patches Link: https://www.romhacking.net/forum/index.php?topic=27346.0
* Credit to PowerPanda for some of the patches from the Revisited mods for Zero 1 and 2
  * Patch Links
    * https://www.romhacking.net/hacks/7115/
    * https://www.romhacking.net/hacks/7119/
* Credit to SCD for the blood restoration mods for Zero 1, 2, and 3
  * Patch Links
    * https://www.romhacking.net/hacks/3723/
    * https://www.romhacking.net/hacks/3738/
    * https://www.romhacking.net/hacks/3741/
* Credit to emerilfryer for the blood and vocal restoration for Zero 4
  * Patch Link: https://www.romhacking.net/hacks/4228/
* Credit to acediez and PowerPanda for documenting offsets for various things
  * https://www.romhacking.net/forum/index.php?topic=27346.0
* Credit to myself for finding the offset for Zero 3 Cyber-Elf costs and Zero 4 Croire level up costs
  * For the US Zero 3 ROM at least, it's at 0x36E2C4 and lasts until offset 0x36E30B
  * For the US Zero 4 ROM at least, it's at 0x886198 and lasts until offset 0x8861A5