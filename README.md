# CS358-Photobooth
For use with Raspberry Pi 5

## TODO
- [X] Create basic frontend script to manage taking and saving pictures
- [X] Create basic backend script to manage grabbing and sending pictures
- [X] Use external push button to take picture
- [X] Flash light when picture is taken
- [ ] Combine frontend and backend scripts (merge both into main)
- [X] Create a script to manage both frontend and backend scripts simultaniously
- [X] Create QR code to photobooth form
- [X] Display key to user after session
- [X] Display QR code to user after session
- [X] Allow user to take up to 5 pictures
- [X] Allow user to stop taking pictures before 5 are taken
- [X] Home screen, gives user basic use instructions
- [ ] Make QR code auto generate for a given forms link

### Libraries used
#### Frontend:
- opencv
  - https://pypi.org/project/opencv-python/
- pyautogui
  - https://pypi.org/project/PyAutoGUI/
- numpy
  - https://pypi.org/project/numpy/

#### Backend:
- pandas
  - https://pypi.org/project/pandas/
- google-api
  - https://pypi.org/project/google-api-python-client/
- oauth2client
  - https://pypi.org/project/oauth2client/
