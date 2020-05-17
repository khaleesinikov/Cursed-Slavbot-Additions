package DiscordBot;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import org.javacord.api.entity.activity.Activity;
import org.javacord.api.entity.message.MessageAuthor;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.javacord.api.entity.user.User;
import org.javacord.api.event.message.MessageCreateEvent;
import org.javacord.api.exception.MissingPermissionsException;
import org.javacord.api.listener.message.MessageCreateListener;
import org.javacord.api.util.logging.ExceptionLogger;

public class Whomst implements MessageCreateListener {

	@Override
	public void onMessageCreate(MessageCreateEvent event) {
		SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd");
		List<User> mentions = event.getMessage().getMentionedUsers();
		if (event.getMessageContent().startsWith("s!whomst")) {
			if (mentions.isEmpty()) {
				MessageAuthor author = event.getMessage().getAuthor();
				EmbedBuilder embed = new EmbedBuilder().setTitle("Who am I?")
						.setColor(author.asUser().get().getRoleColor(event.getServer().get()).get())
						.setThumbnail(author.getAvatar()).addField("Display Name", author.getDisplayName(), true)
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
					embed.addField("Discord Join Date", formatter.format(Date.from(user.getCreationTimestamp())), true);
					if (user.getStatus().getStatusString() == "offline") {
						embed.addField("Connected Clients", "none", true);
					} else
						embed.addField("Connected Clients", user.getCurrentClients().toString(), true);
				});
				// Send the embed. It logs every exception, besides missing permissions (you are
				// not allowed to send message in the channel)
				event.getChannel().sendMessage(embed)
						.exceptionally(ExceptionLogger.get(MissingPermissionsException.class));
			} else {
				User target = mentions.get(0);
				EmbedBuilder embed = new EmbedBuilder().setTitle("Who am I?")
						.setColor(target.getRoleColor(event.getServer().get()).get())
						.setThumbnail(target.getAvatar()).addField("Display Name", target.getDisplayName(event.getServer().get()), true)
						.addField("Name + Discriminator", target.getDiscriminatedName(), true)
						.addField("User Id", target.getIdAsString(), true)
						.addField("Is Bot?", String.valueOf(target.isBot()), true);
				// Keep in mind that a message author can either be a webhook or a normal user
					embed.addField("Online Status", target.getStatus().getStatusString(), true);
					// The User#getActivity() method returns an Optional
					embed.addField("Activity", target.getActivity().map(Activity::getName).orElse("none"), true);
					String joinTimestamp = String.valueOf(target.getJoinedAtTimestamp(event.getServer().get()).get());
					embed.addField("Server Join Date", joinTimestamp.substring(0, 10), true);
					embed.addField("Discord Join Date", formatter.format(Date.from(target.getCreationTimestamp())), true);
					if (target.getStatus().getStatusString() == "offline") {
						embed.addField("Connected Clients", "none", true);
					} else
						embed.addField("Connected Clients", target.getCurrentClients().toString(), true);
				// Send the embed. It logs every exception, besides missing permissions (you are
				// not allowed to send message in the channel)
				event.getChannel().sendMessage(embed)
						.exceptionally(ExceptionLogger.get(MissingPermissionsException.class));
			}
		}

	}

	/*
	 * private Color colorRandomiser() { ArrayList<Color> colour = new
	 * ArrayList<>(); colour.add(Color.BLACK); colour.add(Color.BLUE);
	 * colour.add(Color.CYAN); colour.add(Color.GRAY); colour.add(Color.GREEN);
	 * colour.add(Color.MAGENTA); colour.add(Color.ORANGE); colour.add(Color.PINK);
	 * colour.add(Color.RED); colour.add(Color.WHITE); colour.add(Color.YELLOW);
	 * Collections.shuffle(colour); return colour.get(0); }
	 */

}
