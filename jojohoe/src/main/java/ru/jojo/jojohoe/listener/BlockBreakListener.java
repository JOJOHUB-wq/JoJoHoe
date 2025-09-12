package ru.jojo.jojohoe.listener;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.minimessage.MiniMessage;
import org.bukkit.GameMode;
import org.bukkit.block.Block;
import org.bukkit.block.data.Ageable;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.inventory.ItemStack;
import ru.jojo.jojohoe.manager.ConfigManager;
import ru.jojo.jojohoe.manager.HoeManager;
import ru.jojo.jojohoe.model.HoeLevel;

public class BlockBreakListener implements Listener {

    private final ConfigManager configManager;
    private final HoeManager hoeManager;

    public BlockBreakListener(ConfigManager configManager, HoeManager hoeManager) {
        this.configManager = configManager;
        this.hoeManager = hoeManager;
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onBlockBreak(BlockBreakEvent event) {
        Player player = event.getPlayer();
        Block block = event.getBlock();
        ItemStack itemInHand = player.getInventory().getItemInMainHand();

        if (player.getGameMode() == GameMode.CREATIVE) {
            return;
        }

        if (!hoeManager.isSpecialHoe(itemInHand)) {
            return;
        }

        if (!player.hasPermission("jojohoe.use")) {
            if (configManager.getSetting("notify_on_no_permission")) {
                player.sendMessage(configManager.getMessage("cant_use"));
            }
            return;
        }

        if (!configManager.getSupportedCrops().contains(block.getType())) {
            return;
        }

        if (!(block.getBlockData() instanceof Ageable ageable)) {
            return;
        }

        if (ageable.getAge() != ageable.getMaximumAge()) {
            return;
        }

        hoeManager.handleCropBreak(player, itemInHand, block);

        if (configManager.getSetting("show_progress_message")) {
            String levelId = hoeManager.getHoeLevelId(itemInHand);
            if (levelId == null) return;

            HoeLevel currentLevel = configManager.getLevel(levelId);
            if (currentLevel == null) return;

            // Don't show progress bar if max level is reached
            if (configManager.getNextLevel(levelId) == null) {
                return;
            }

            long progress = hoeManager.getHoeProgress(itemInHand);
            long required = currentLevel.requiredCrops();

            String progressBarMessage = configManager.getMessage("progress_bar",
                "progress", String.valueOf(progress),
                "required", String.valueOf(required)
            );
            // We remove the prefix for action bar messages as it can be intrusive.
            progressBarMessage = progressBarMessage.replace(configManager.getMessage("prefix"), "");

            player.sendActionBar(MiniMessage.miniMessage().deserialize(progressBarMessage));
        }
    }
}
