# AITA to TTS to Video
I've built a quick and simple script to pull the top posts of AITA from Reddit. Once it grabs the post, I scrape the Title, Post, Date, Author, and comments.

I then feed the data to a TTS library from Python (Pyttsx3) and it creates an audio file. I then feed this audio file to MoviePy which converts it to a video that I can use and post!