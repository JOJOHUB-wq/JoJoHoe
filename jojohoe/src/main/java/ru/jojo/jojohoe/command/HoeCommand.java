package ru.jojo.jojohoe.command;

import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.jetbrains.annotations.NotNull;
import ru.jojo.jojohoe.manager.ConfigManager;
import ru.jojo.jojohoe.manager.HoeManager;
import ru.jojo.jojohoe.model.HoeLevel;

import java.util.HashMap;

public class HoeCommand implements CommandExecutor {

    private final ConfigManager configManager;
    private final HoeManager hoeManager;

    public HoeCommand(ConfigManager configManager, HoeManager hoeManager) {
        this.configManager = configManager;
        this.hoeManager = hoeManager;
    }

    @Override
    public boolean onCommand(@NotNull CommandSender sender, @NotNull Command command, @NotNull String label, @NotNull String[] args) {
        if (args.length == 0) {
            sender.sendMessage(configManager.getMessage("usage"));
            return true;
        }

        String subCommand = args[0].toLowerCase();

        if (subCommand.equals("reload")) {
            handleReload(sender);
            return true;
        }

        handleGive(sender, args);
        return true;
    }

    private void handleReload(CommandSender sender) {
        if (!sender.hasPermission("jojohoe.reload")) {
            sender.sendMessage(configManager.getMessage("no_permission"));
            return;
        }
        configManager.reload();
        sender.sendMessage(configManager.getMessage("reload"));
    }

    private void handleGive(CommandSender sender, String[] args) {
        Player target = null;
        String levelId = null;

        if (args.length == 1) {
            if (!(sender instanceof Player player)) {
                sender.sendMessage(configManager.getMessage("player_not_found"));
                return;
            }
            target = player;
            levelId = args[0];
            if (!sender.hasPermission("jojohoe.give.self")) {
                sender.sendMessage(configManager.getMessage("no_permission"));
                return;
            }
        } else if (args.length >= 2) {
            target = Bukkit.getPlayer(args[0]);
            levelId = args[1];
            if (!sender.hasPermission("jojohoe.give.others")) {
                sender.sendMessage(configManager.getMessage("no_permission"));
                return;
            }
        }

        if (target == null) {
            sender.sendMessage(configManager.getMessage("player_not_found"));
            return;
        }

        HoeLevel level = configManager.getLevel(levelId);
        if (level == null) {
            sender.sendMessage(configManager.getMessage("level_not_found", "id", levelId));
            return;
        }

        ItemStack hoe = hoeManager.createHoe(level.id());
        if (hoe == null) {
            return;
        }

        final Player finalTarget = target;
        HashMap<Integer, ItemStack> leftover = finalTarget.getInventory().addItem(hoe);
        if (!leftover.isEmpty()) {
            leftover.values().forEach(item -> finalTarget.getWorld().dropItemNaturally(finalTarget.getLocation(), item));
            finalTarget.sendMessage(configManager.getMessage("inventory_full"));
        }

        if (finalTarget.equals(sender)) {
            sender.sendMessage(configManager.getMessage("hoe_given_self"));
        } else {
            sender.sendMessage(configManager.getMessage("hoe_given_other", "player", finalTarget.getName()));
        }
    }
}
