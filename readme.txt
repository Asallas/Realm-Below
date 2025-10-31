Worked alone.
All sprite model assets created by SmallScaleInt: https://smallscaleint.itch.io
List of all items developed:
- Player class
    - Player can attack, roll, block, and move around
    - Attacks all share same hitbox, still need to finetune for different attacks and directions
    - Rolling creates i-frames which make you immune to damage
    - Blocking is just visual and has no actual function yet
- MeleeEnemy class
    - Basic AI that follows the center of the player's rect and attacks when it gets within a certain range
    - Has one working attack at the moment that still needs hitbox finetuning
    - Low priority to add more
- RangeEnemy class
    - AI will try to stay within a certain range away from the player
    - Spawns a single projectile during attack animation
    - Low priority to add more attacks
- Boss class
    - Model has changed when compared to Milestone 1 to better fit the rest of the sprites
    - Copies the same movement AI as MeleeEnemy just moves slower
    - High priority to add actual Boss mechanics with more implemented moves and require an actual strategy
- projectiles class
    - Placeholder model is just a red ball
    - Spawns in and follows a line through the target position
    - does not update target position which would allow for player tracking
    - High priority to find a proper model instead of a ball
    - Low priority to add varient that does player tracking
- All sprites can take damage, deal damage, and die. When player dies it's a game over and when all enemies die it is a simple win screen
- Still need to add proper environment, current green color is just a placeholder background

Controls:
- Arrow keys to move around
- 'g' to block, holding keeps player in a 'blocking' state
- 'w' and 'q' are the attacks a player can use
- 'z' is a 'counter' that functions the same as attacks at the moment
- 'LSHIFT' is a roll which moves the player the opposite direction they are facing and removes their hitbox temporarily
- 'ESC' quits the game