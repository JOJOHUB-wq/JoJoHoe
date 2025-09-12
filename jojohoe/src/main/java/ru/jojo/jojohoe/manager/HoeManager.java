package ru.jojo.jojohoe.manager;

import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.TextDecoration;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.block.Block;
import org.bukkit.enchantments.Enchantment;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataContainer;
import org.bukkit.persistence.PersistentDataType;
import ru.jojo.jojohoe.JoJoHoe;
import ru.jojo.jojohoe.model.HoeLevel;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

public class HoeManager {

    private final JoJoHoe plugin;
    private final ConfigManager configManager;
    private final Random random = new Random();

    public final NamespacedKey specialHoeKey;
    public final NamespacedKey levelKey;
    public final NamespacedKey progressKey;

    private static final Map<Material, Material> CROP_TO_DROP_MAP = new HashMap<>();
    static {
        CROP_TO_DROP_MAP.put(Material.WHEAT, Material.WHEAT);
        CROP_TO_DROP_MAP.put(Material.POTATOES, Material.POTATO);
        CROP_TO_DROP_MAP.put(Material.CARROTS, Material.CARROT);
        CROP_TO_DROP_MAP.put(Material.BEETROOTS, Material.BEETROOT);
        CROP_TO_DROP_MAP.put(Material.NETHER_WART, Material.NETHER_WART);
        CROP_TO_DROP_MAP.put(Material.COCOA, Material.COCOA_BEANS);
        CROP_TO_DROP_MAP.put(Material.SWEET_BERRY_BUSH, Material.SWEET_BERRIES);
        CROP_TO_DROP_MAP.put(Material.TORCHFLOWER_CROP, Material.TORCHFLOWER);
        CROP_TO_DROP_MAP.put(Material.PITCHER_CROP, Material.PITCHER_POD);
    }

    public HoeManager(JoJoHoe plugin, ConfigManager configManager) {
        this.plugin = plugin;
        this.configManager = configManager;
        this.specialHoeKey = new NamespacedKey(plugin, "special_hoe");
        this.levelKey = new NamespacedKey(plugin, "hoe_level");
        this.progressKey = new NamespacedKey(plugin, "hoe_progress");
    }

    public ItemStack createHoe(String levelId) {
        HoeLevel level = configManager.getLevel(levelId);
        if (level == null) {
            return null;
        }

        ItemStack hoe = new ItemStack(level.material());
        ItemMeta meta = hoe.getItemMeta();

        meta.displayName(Component.text(configManager.getFormattedName(level)).decoration(TextDecoration.ITALIC, false));
        meta.lore(getLoreComponents(level, 0));

        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        pdc.set(specialHoeKey, PersistentDataType.BOOLEAN, true);
        pdc.set(levelKey, PersistentDataType.STRING, level.id());
        pdc.set(progressKey, PersistentDataType.LONG, 0L);

        hoe.setItemMeta(meta);

        applyEnchantments(hoe, level.enchants());

        return hoe;
    }

    public void handleCropBreak(Player player, ItemStack hoe, Block block) {
        if (hoe == null || !isSpecialHoe(hoe)) {
            return;
        }

        ItemMeta meta = hoe.getItemMeta();
        PersistentDataContainer pdc = meta.getPersistentDataContainer();

        String currentLevelId = pdc.get(levelKey, PersistentDataType.STRING);
        HoeLevel currentLevel = configManager.getLevel(currentLevelId);
        if (currentLevel == null) return;

        if (currentLevel.fortuneBonus() > 0) {
            int bonusAmount = random.nextInt(currentLevel.fortuneBonus() + 1);
            if (bonusAmount > 0) {
                Material dropType;
                if (block.getType() == Material.WHEAT) {
                    // Special case for wheat to only drop extra WHEAT, not seeds.
                    dropType = Material.WHEAT;
                } else {
                    dropType = CROP_TO_DROP_MAP.get(block.getType());
                }

                if (dropType != null) {
                    block.getWorld().dropItemNaturally(block.getLocation(), new ItemStack(dropType, bonusAmount));
                }
            }
        }

        HoeLevel nextLevel = configManager.getNextLevel(currentLevelId);
        if (nextLevel == null) {
            return;
        }

        long currentProgress = pdc.getOrDefault(progressKey, PersistentDataType.LONG, 0L);
        long newProgress = currentProgress + 1;

        if (newProgress >= currentLevel.requiredCrops()) {
            levelUp(hoe, meta, nextLevel);
            player.sendMessage(configManager.getMessage("level_up", "level_name", nextLevel.name()));
        } else {
            pdc.set(progressKey, PersistentDataType.LONG, newProgress);
            meta.lore(getLoreComponents(currentLevel, newProgress));
            hoe.setItemMeta(meta);
        }
    }

    private void levelUp(ItemStack hoe, ItemMeta meta, HoeLevel newLevel) {
        PersistentDataContainer pdc = meta.getPersistentDataContainer();
        pdc.set(levelKey, PersistentDataType.STRING, newLevel.id());
        pdc.set(progressKey, PersistentDataType.LONG, 0L);

        hoe.setType(newLevel.material());
        meta.displayName(Component.text(configManager.getFormattedName(newLevel)).decoration(TextDecoration.ITALIC, false));
        meta.lore(getLoreComponents(newLevel, 0));

        hoe.setItemMeta(meta);

        hoe.getEnchantments().keySet().forEach(hoe::removeEnchantment);
        applyEnchantments(hoe, newLevel.enchants());
    }

    private void applyEnchantments(ItemStack item, Map<Enchantment, Integer> enchantments) {
        if (enchantments != null && !enchantments.isEmpty()) {
            item.addUnsafeEnchantments(enchantments);
        }
    }

    public boolean isSpecialHoe(ItemStack item) {
        if (item == null || !item.hasItemMeta()) {
            return false;
        }
        return item.getItemMeta().getPersistentDataContainer().has(specialHoeKey, PersistentDataType.BOOLEAN);
    }

    public String getHoeLevelId(ItemStack item) {
        if (!isSpecialHoe(item)) return null;
        return item.getItemMeta().getPersistentDataContainer().get(levelKey, PersistentDataType.STRING);
    }

    public long getHoeProgress(ItemStack item) {
        if (!isSpecialHoe(item)) return 0;
        return item.getItemMeta().getPersistentDataContainer().getOrDefault(progressKey, PersistentDataType.LONG, 0L);
    }

    private List<Component> getLoreComponents(HoeLevel level, long progress) {
        return configManager.getFormattedLore(level, progress).stream()
                .map(line -> Component.text(line).decoration(TextDecoration.ITALIC, false))
                .collect(Collectors.toList());
    }
}
