# ChatDash

## About

ChatDash is an app created with [Dash](https://dash.plot.ly/) for analysing chat data which has been exported from WhatsApp. The analysis include (for now):
* Overall number of messages
* Busiest month of the year, day of the week, time of the day
* User responding patterns
* Group's favourite emojis
* Media sharing patterns
* Word cloud
* Random messages turned in random inspirational quotes

### How to locally run this app

```
git clone https://github.com/natworks/chat_analysis
cd chat_analysis
python3 -m virtualenv chatenv

```

Install requirements:
```
pip install -r requirements.txt
```

Run:
```
python app.py
```

### Screenshot

![screenshot](assets/screenshot.png)

### Resources

* The app layout has been (**heavily**) inspired by [Clinical Analytics Dashboard](https://dash.gallery/dash-clinical-analytics/)
* Parsing Whatsapp files has been made robust by using parts of the code available in [whatstk's parser](https://github.com/lucasrodes/whatstk/blob/main/whatstk/whatsapp/parser.py)
* Images for generating the quote come from [unsplash](https://unsplash.com)