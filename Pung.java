package DiscordBot;

import java.util.Random;

import org.javacord.api.DiscordApi;
import org.javacord.api.event.message.MessageCreateEvent;
import org.javacord.api.listener.message.MessageCreateListener;

public class Pung implements MessageCreateListener {
	
	DiscordApi api;
	Random r = new Random();
	
	public Pung(DiscordApi api) {
		this.api = api;
	}
	
	@Override
	public void onMessageCreate(MessageCreateEvent event) {
		if(event.getMessage().getMentionedUsers().contains(api.getYourself())) {
			int emote = r.nextInt(4);
			switch(emote) {
			case 0:
				event.getChannel().sendMessage("<:pung:697884021304066139>");
				break;
			case 1:
				event.getChannel().sendMessage("<:pepeping:697889678598340668>");
				break;
			case 2:
				event.getChannel().sendMessage("<:angeryping:697889718536372246>");
				break;
			case 3:
				event.getChannel().sendMessage("<:pingblob:697890269223321670>");
				break;
			}
			
		}
	}

}
