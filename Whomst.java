package DiscordBot;

import java.awt.Color;
import org.javacord.api.entity.activity.Activity;
import org.javacord.api.entity.message.MessageAuthor;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.javacord.api.event.message.MessageCreateEvent;
import org.javacord.api.exception.MissingPermissionsException;
import org.javacord.api.listener.message.MessageCreateListener;
import org.javacord.api.util.logging.ExceptionLogger;

public class Whomst implements MessageCreateListener {
	
	@Override
	public void onMessageCreate(MessageCreateEvent event) {
        if(event.getMessageContent().equalsIgnoreCase("s!whomst")) {
            MessageAuthor author = event.getMessage().getAuthor();
            EmbedBuilder embed = new EmbedBuilder()
                    .setTitle("Who am I?")
                    .setColor(Color.CYAN)
                    .setThumbnail(author.getAvatar())
                    .addField("Display Name", author.getDisplayName(), true)
                    .addField("Name + Discriminator", author.getDiscriminatedName(), true)
                    .addField("User Id", author.getIdAsString(), true)
                    .addField("Is Bot?", String.valueOf(author.isBotUser()), true);
            // Keep in mind that a message author can either be a webhook or a normal user
            author.asUser().ifPresent(user -> {
                embed.addField("Online Status", user.getStatus().getStatusString(), true);
                // The User#getActivity() method returns an Optional
                embed.addField("Activity", user.getActivity().map(Activity::getName).orElse("none"), true);
                String joinTimestamp = String.valueOf(user.getJoinedAtTimestamp(event.getServer().get()).get());
                embed.addField("Server Join Date", joinTimestamp.substring(0, 10), true);
                if(user.getStatus().getStatusString() == "offline") {
                	embed.addField("Connected Clients", "none", true);
                } else
                	embed.addField("Connected Clients", user.getCurrentClients().toString(), true);
            });
            // Send the embed. It logs every exception, besides missing permissions (you are not allowed to send message in the channel)
            event.getChannel().sendMessage(embed)
                    .exceptionally(ExceptionLogger.get(MissingPermissionsException.class));
        }
        
    }

}
