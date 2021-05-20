# **BDO Loot to Sheet**
This program will take your in-game screenshot(s) and process it directly into your spreadsheet.

## How to use?

1) Click on the 'Upload Images' button to upload the image(s) you want to process.
2) Click on the 'Process images' button to process the image(s).


## How to run? [WIP]
Requires Python 3.9.4.

## How does it work?

- After pressing the `Process images` button, the program will do the following:
  1) Locate your inventory items via TemplateMatching with a preloaded template that finds your `Auto Arrange` checkbox.
  2) For each slot, an object will be added to an array, that object will contain a small scale image (50x50) of the item and some extra data required.
  3) Go over the item array and match each item to the templates provided.
  4) Reach out to a DB of items, and check if the items are stackable or not.
  5) If the items are stackable, it will find the amount of items you hold.
  6) Update a spreadsheet with the data it acquired from the image.


## LIMITATIONS:

- Requires full visability of the inventory tab.
- Requires UI Scaling of **100%** (default).
