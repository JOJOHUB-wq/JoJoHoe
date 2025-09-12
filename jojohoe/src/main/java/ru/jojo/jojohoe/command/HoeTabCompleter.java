package ru.jojo.jojohoe.command;

import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;
import org.bukkit.util.StringUtil;
import org.jetbrains.annotations.NotNull;
import ru.jojo.jojohoe.manager.ConfigManager;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class HoeTabCompleter implements TabCompleter {

    private final ConfigManager configManager;

    public HoeTabCompleter(ConfigManager configManager) {
        this.configManager = configManager;
    }

    @Override
    public List<String> onTabComplete(@NotNull CommandSender sender, @NotNull Command command, @NotNull String alias, @NotNull String[] args) {
        List<String> completions = new ArrayList<>();
        List<String> suggestions = new ArrayList<>();

        if (args.length == 1) {
            if (sender.hasPermission("jojohoe.reload")) {
                suggestions.add("reload");
            }
            if (sender.hasPermission("jojohoe.give.self")) {
                suggestions.addAll(configManager.getLevelIds());
            }
            if (sender.hasPermission("jojohoe.give.others")) {
                suggestions.addAll(Bukkit.getOnlinePlayers().stream().map(Player::getName).collect(Collectors.toList()));
            }
            StringUtil.copyPartialMatches(args[0], suggestions, completions);
        } else if (args.length == 2) {
            // Suggest level IDs for the second argument if the user might be giving a hoe to another player.
            if (sender.hasPermission("jojohoe.give.others")) {
                suggestions.addAll(configManager.getLevelIds());
            }
            StringUtil.copyPartialMatches(args[1], suggestions, completions);
        }

        return completions;
    }
}
