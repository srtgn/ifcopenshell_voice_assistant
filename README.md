# **Voice Assistant For BIM**
## Design Driven Project - Final Documentation
------
### *Beyzanur Kaya, Saeed Rastegarian*
<br/>


## **Definition**<br/>

### Problem :
Software dependency on BIM and difficulties on using software, such as hardship on being an expert and interaction for non-BIM users

### Oppurtunity :
A software depends on open source BIM and voice interaction not only will make data extraction from model possible, but easily will decrease the data loss from design office to construction site. <br/>
Site workers can reach more understable information easily; architects can reach out to data any place; complicated data extractions or model controls can be downsized to basic voice message.  <br/>
Non-BIM experts can interact with the model, this will improve data transitition. <br/> 


## To Run the Software You Need This Dependencies
- IFCOpenShell (BIM Module)
- Numpy
- Apiai
- Speech_recognition as sr (Speech Recognition)
- re
- pyttsx3
- webbrowser


## **How to Run**
Create a python environment with version **3.6**, sr only works with python 3.6<br/>
Make sure your environment has all dependencies<br/>
Run it and click, **click me** button, you will hear assistant is guiding you<br/>
**Closest point to origin** refers to the corner which wall is closest to origin, when a distance ask please don't hesitate to take **closest point to origin** as reference


## Command Variety
IfcOpenShell Voice Assistant, creates command and extract data from Ifc Models with IFC OpenShell Python commands. Possible commands with voice assistant are;
- Create Wall
- Open a file
- Set a Height Limit
- Extract number of elements (wall, window and door)


## Voice Recognition
- To run the voice recognition module from Google smoothly, please try to talk longer, instead of just saying vocablaries create full sentences. E.g. Instead of "open", please try "Can you please open a file"<br/>
- Wait one second before speaking and try not to locate key word in the middle of sentence. <br/>
- When giving certain vocablaries create a context, voice recognition understands it better. E.g. say "Can you create a partition wall" instead of "wall", say "number 6" or "6 meters" when specifying number, don't forget if you state decimal point such as "six point zero" results will be more precise. <br/>


## IFC Viewer 
Current IFC viewer is embedded version of [ifcjs](https://github.com/IFCjs/web-ifc-viewer), <br/>
It is a js oriented web viewer, you can test or use it with the [link](https://ifcjs.github.io/web-ifc-viewer/example/index)<br/>
To use viewer click the file icon on viewer and select the Ifc File, you may need to refresh page to refresh model