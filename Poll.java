package DiscordBot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.message.Message;
import org.javacord.api.entity.message.Reaction;
import org.javacord.api.entity.message.embed.Embed;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.javacord.api.entity.message.embed.EmbedField;
import org.javacord.api.entity.user.User;
import org.javacord.api.event.message.MessageCreateEvent;
import org.javacord.api.listener.message.MessageCreateListener;

public class Poll implements MessageCreateListener {

	DiscordApi api;
	String help = "```For a simple poll just use 's!poll {question}' to get a yes/no poll\n"
			+ "For custom options use 's!poll -o {question}; {option1}, ... {option10}'\n"
			+ "For custom emojis use 's!poll -e {question}; {option1}, {emoji1}, ... {option10}, {emoji10}'\n"
			+ "To tally results use 's!tally {poll ID}'```";
	String[] optionNumbers = { "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟" };

	public Poll(DiscordApi api) {
		this.api = api;
	}

	@Override
	public void onMessageCreate(MessageCreateEvent event) {
		if (event.getMessageContent().equalsIgnoreCase("s!pollhelp")) {
			event.getChannel().sendMessage(help);
			return;
		}
		if (event.getMessageContent().startsWith("s!poll ")) {
			String message = event.getMessage().getContent();
			try {
				message = message.substring(7);
			} catch (StringIndexOutOfBoundsException se) {
				event.getChannel().sendMessage("Your poll needs a question!");
				return;
			}
			String[] options;
			boolean basic = false;
			boolean emoji = false;
			if (message.startsWith("-e ")) {
				emoji = true;
				message = message.substring(3);
				String[] question = message.split("; ");
				try {
					message = question[0];
					options = question[1].split(", ");
				} catch (ArrayIndexOutOfBoundsException ae) {
					event.getChannel().sendMessage("I don't understand your formatting! Use s!pollhelp for instructions.");
					return;
				}
				if (options.length % 2 != 0) {
					event.getChannel().sendMessage("You appear to have missed out an option or emoji.");
					return;
				}
				if (options.length < 4) {
					event.getChannel().sendMessage("Fun fact, if you only have one option that's not a poll.");
					return;
				}
				if (options.length > 20) {
					event.getChannel().sendMessage("Too many options! The maximum number this bot supports is 10.");
					return;
				}
				if (checkDuplicateEmojis(options)) {
					event.getChannel().sendMessage("You can't use the same emoji for multiple options you silly goose.");
					return;
				}
			} else if (message.startsWith("-o ")) {
				message = message.substring(3);
				String[] question = message.split("; ");
				try {
					message = question[0];
					options = question[1].split(", ");
				} catch (ArrayIndexOutOfBoundsException ae) {
					event.getChannel().sendMessage("I don't understand your formatting! Use s!pollhelp for instructions.");
					return;
				}
				if (options.length < 2) {
					event.getChannel().sendMessage("Fun fact, if you only have one option that's not a poll.");
					return;
				}
				if (options.length > 10) {
					event.getChannel().sendMessage("Too many options! The maximum number this bot supports is 10.");
					return;
				}
			} else {
				basic = true;
				options = new String[] { "Yes", "No" };
			}
			EmbedBuilder poll = new EmbedBuilder().setTitle(message)
					.setDescription("Created by: " + event.getMessageAuthor().getName());
			if (basic) {
				poll.addField("👍", "Yes", true);
				poll.addField("👎", "No", true);
			} else if (!emoji) {
				for (int i = 0; i < options.length; i++)
					poll.addField(optionNumbers[i], options[i]);
			} else {
				for (int i = 0; i< options.length-1; i+=2)
					poll.addField(options[i+1], options[i]);
			}
			Message m = event.getChannel().sendMessage(poll).join();
			if (basic) {
				m.addReaction("👍").join();
				m.addReaction("👎").join();
			} else if (!emoji) {
				for (int i = 0; i < options.length; i++)
					m.addReaction(optionNumbers[i]).join();
			} else {
				for (int i = 1; i < options.length; i+=2) {
					m.addReaction(options[i]);
				}
			}
			poll.setFooter("Poll ID: " + m.getIdAsString());
			m.edit(poll);
		}

		// ------------ TALLY PART BEGINS HERE ------------

		if (event.getMessageContent().startsWith("s!tally")) {
			String message = event.getMessage().getContent();
			try {
				message = message.substring(8);
			} catch (StringIndexOutOfBoundsException se) {
				event.getChannel().sendMessage("Missing poll ID.");
				return;
			}
			Message m = null;
			try {
				m = event.getChannel().getMessageById(message).join();
			} catch (Exception e) {
				event.getChannel().sendMessage("Poll not found in this channel.");
				return;
			}
			if (!m.getAuthor().isYourself() || m.getEmbeds().isEmpty()) {
				event.getChannel().sendMessage("Message ID does not lead to a valid poll.");
				return;
			}
			Embed poll = m.getEmbeds().get(0);
			if (!poll.getFooter().isPresent()) {
				event.getChannel().sendMessage("Message ID does not lead to a valid poll.");
				return;
			}
			if (!poll.getFooter().get().getText().get().startsWith("Poll ID: ")) {
				event.getChannel().sendMessage("Message ID does not lead to a valid poll.");
				return;
			}
			
			List<EmbedField> fields = poll.getFields();
			HashMap<String, String> options = new HashMap<>();
			ArrayList<Reaction> reacts = new ArrayList<Reaction>();
			for (EmbedField ef : fields) {
				options.put(ef.getName(), ef.getValue());
				reacts.add(m.getReactionByEmoji(ef.getName()).get());
			}
			HashMap<String, Integer> totals = new HashMap<>();
			for (Reaction r : reacts) {
				Integer counter = 0;
				try {
					for (User u : r.getUsers().get())
						if (!u.isBot())
							counter++;
				} catch (InterruptedException | ExecutionException e) {
					System.err.println("I'm impressed you managed to trigger this error");
					e.printStackTrace();
					return;
				}
				totals.put(r.getEmoji().asUnicodeEmoji().orElse(r.getEmoji().toString()), counter);
			}
			EmbedBuilder tally = new EmbedBuilder().setTitle("Results for: " + poll.getTitle().get())
					.setDescription(poll.getDescription().get());
			for (EmbedField ef : fields)
				tally.addField(ef.getName() + " " + options.get(ef.getName()), String.valueOf(totals.get(ef.getName())));
			event.getChannel().sendMessage(tally);
		}
	}
	
	private boolean checkDuplicateEmojis(String[] options) {
		Set<String> duplicatesNames = new HashSet<String>();
		Set<String> testSet = new HashSet<String>();
		for(int i = 1; i<options.length; i+=2){
		    boolean check = testSet.add(options[i]);
		    if(!check){
		        duplicatesNames.add(options[i]);
		    }
		}
		if (duplicatesNames.isEmpty())
			return false;
		return true; //true if duplicate emojis ARE found
	}

}
