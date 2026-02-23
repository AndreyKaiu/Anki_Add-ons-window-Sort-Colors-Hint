# Anki_Add-ons-window-Sort-Colors-Hint
Add-on for the Anki program. For the window with add-ons, it implements the ability to sort and color the list, it is possible to set a hint for a specific add-on.

**Changes for version 1.4**

The restart algorithm has been corrected as much as possible. I had to do this because the launcher was released last year. And now even the AI ​​suggests installing the add-on if it works properly: [AnkiRestart V2 - Quick Anki Rebooter](https://ankiweb.net/shared/info/1766024579) 

I can't say for sure how accurate the AI ​​code was, but this algorithm works fine on my Windows 10. Give it a try.

**Changes for version 1.3**

Ability to quickly load a profile of allowed add-ons. After selecting a profile, you can quickly restart the anki program using the hotkeys Alt+Shift+F4
![Anki_Add-ons-window-Sort-Colors-Hint_1_3_1](https://github.com/user-attachments/assets/6da5ff52-ca50-4bfe-8265-4bffdd2b5306)

After pressing the "Restore Defaults" button, 2 buttons may be displayed allowing you to quickly move to the line highlighted in red. This is how duplicate lines are shown if the user has previously changed something to suit his preferences and he is now given the opportunity to delete the extra lower (new) line if he needs to leave the value as it was before.
![Anki_Add-ons-window-Sort-Colors-Hint_1_3_2](https://github.com/user-attachments/assets/334efe8a-077d-4d86-b75a-77ab87a26ffd)


**Changes for version 1.0-1.2**

![Anki_Add-ons window_v10_01](https://github.com/user-attachments/assets/c744b2df-86dc-4aec-a8cc-fdb9e61868ee)
![Anki_Add-ons window_v10_02](https://github.com/user-attachments/assets/5d5c1857-d789-45bd-a6d9-8fd2df98a1a1)
![Anki_Add-ons window_v10_03](https://github.com/user-attachments/assets/5fd6102d-c4cd-4392-9e5f-a9defc8827e9)
![Anki_Add-ons window_v10_04](https://github.com/user-attachments/assets/aaa83b61-6242-42f5-9b5c-e66cabc0af49)
![Anki_Add-ons window_v12_05](https://github.com/user-attachments/assets/595f3da8-10ee-4927-aefd-ed645d37ccf3)


All this functionality simplifies working with add-ons, since you can highlight important ones with color, you can set a hint after the name or a hint before the name (group name). Sorting allows you to see which add-ons are newer (older) or with which add-on we recently changed the setting (changing the color, hint does not change the date of the meta.json file, although it stores this information there).

If you have a question or suggestion, do not create an issue on this site, but go to the dedicated topic [on the forum](https://forums.ankiweb.net/t/add-ons-window-sort-colors-hint-official-support/58646)

**VERSIONS**
- 1.4, date: 2026-02-22. The restart algorithm has been corrected as much as possible. Fixed display in transparent color.
- 1.3, date: 2025-05-26. Ability to quickly load a profile of allowed add-ons. After selecting a profile, you can quickly restart the anki program using the hotkeys Alt+Shift+F4 After pressing the "Restore Defaults" button, 2 buttons may be displayed allowing you to quickly move to the line highlighted in red. This is how duplicate lines are shown if the user has previously changed something to suit his preferences and he is now given the opportunity to delete the extra lower (new) line if he needs to leave the value as it was before. Added backward substring search  
- 1.2, date: 2025-04-18. The "Toggle Enabled" action has been duplicated in the context menu and the hotkey F9 has been assigned to it. The editor in the "Config" window has been made with syntax highlighting, and there is now a simple search option.
- 1.1, date: 2025-04-09. Fixed a bug that occurred if the add-on name was None (Thank you [https://ankiweb.net/shared/by-author/2063726776](https://ankiweb.net/shared/by-author/2063726776))
- 1.0, date: 2025-04-07. First release

