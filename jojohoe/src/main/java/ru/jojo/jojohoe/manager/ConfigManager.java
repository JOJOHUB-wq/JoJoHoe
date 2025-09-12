package ru.jojo.jojohoe.manager;

import org.bukkit.ChatColor;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.enchantments.Enchantment;
import ru.jojo.jojohoe.JoJoHoe;
import ru.jojo.jojohoe.model.HoeLevel;

import java.util.*;
import java.util.stream.Collectors;

public class ConfigManager {

    private final JoJoHoe plugin;
    private FileConfiguration config;

    private String prefix;
    private Map<String, String> messages;
    private Map<String, List<String>> formats;
    private Map<String, Boolean> settings;

    private List<HoeLevel> levels;
    private Map<String, HoeLevel> levelsById;
    private final Set<Material> supportedCrops = EnumSet.of(
            Material.WHEAT, Material.POTATOES, Material.CARROTS, Material.BEETROOTS,
            Material.NETHER_WART, Material.TORCHFLOWER_CROP, Material.PITCHER_CROP,
            Material.SWEET_BERRY_BUSH, Material.COCOA
    );

    private boolean recipeEnabled;
    private List<String> recipeShape;
    private Map<Character, Material> recipeIngredients;

    public ConfigManager(JoJoHoe plugin) {
        this.plugin = plugin;
        loadConfig();
    }

    public void reload() {
        plugin.reloadConfig();
        loadConfig();
    }

    private void loadConfig() {
        this.config = plugin.getConfig();
        plugin.saveDefaultConfig();

        loadMessages();
        loadFormats();
        loadSettings();
        loadLevels();
        loadRecipe();
    }

    private void loadMessages() {
        messages = new HashMap<>();
        prefix = getString("messages.prefix", "&8[&bJoJoHoe&8] ");
        ConfigurationSection messagesSection = config.getConfigurationSection("messages");
        if (messagesSection != null) {
            for (String key : messagesSection.getKeys(false)) {
                messages.put(key, getString("messages." + key, ""));
            }
        }
    }

    private void loadFormats() {
        formats = new HashMap<>();
        ConfigurationSection formatSection = config.getConfigurationSection("format");
        if (formatSection != null) {
            formats.put("name", Collections.singletonList(getString("format.name", "&bОсобая мотыга &7({level_name})")));
            formats.put("lore", getStringList("format.lore", List.of("&7Прогресс: &a{progress}&7/&c{required}")));
            formats.put("lore_max_level", getStringList("format.lore_max_level", List.of("&a&lМаксимальный уровень")));
        }
    }

    private void loadSettings() {
        settings = new HashMap<>();
        settings.put("show_progress_message", config.getBoolean("settings.show_progress_message", true));
        settings.put("notify_on_no_permission", config.getBoolean("settings.notify_on_no_permission", true));
    }

    private void loadLevels() {
        levels = new ArrayList<>();
        levelsById = new LinkedHashMap<>();
        List<Map<?, ?>> levelMaps = config.getMapList("levels");
        for (Map<?, ?> levelMap : levelMaps) {
            try {
                String id = (String) levelMap.get("id");
                String name = (String) levelMap.get("name");
                Material material = Material.matchMaterial((String) levelMap.get("material"));

                Object requiredCropsObj = levelMap.get("required_crops");
                long requiredCrops = (requiredCropsObj instanceof Number) ? ((Number) requiredCropsObj).longValue() : 0L;

                Object fortuneBonusObj = levelMap.get("fortune_bonus");
                int fortuneBonus = (fortuneBonusObj instanceof Number) ? ((Number) fortuneBonusObj).intValue() : 0;

                Map<Enchantment, Integer> enchants = new HashMap<>();
                List<String> enchantStrings = (List<String>) levelMap.get("enchants");
                if (enchantStrings != null) {
                    for (String enchantString : enchantStrings) {
                        String[] parts = enchantString.split(":");
                        if (parts.length == 2) {
                            Enchantment ench = Enchantment.getByKey(NamespacedKey.minecraft(parts[0].toLowerCase()));
                            if (ench != null) {
                                enchants.put(ench, Integer.parseInt(parts[1]));
                            }
                        }
                    }
                }

                List<String> lore = (List<String>) levelMap.get("lore");
                HoeLevel level = new HoeLevel(id, name, material, requiredCrops, fortuneBonus, enchants, lore);
                levels.add(level);
                if (id != null) {
                    levelsById.put(id.toLowerCase(), level);
                }
            } catch (Exception e) {
                plugin.getLogger().warning("Failed to load a level: " + e.getMessage());
            }
        }
    }

    private void loadRecipe() {
        recipeEnabled = config.getBoolean("recipe.enabled", false);
        if (!recipeEnabled) return;

        recipeShape = config.getStringList("recipe.shape");
        recipeIngredients = new HashMap<>();
        ConfigurationSection ingredientsSection = config.getConfigurationSection("recipe.ingredients");
        if (ingredientsSection != null) {
            for (String key : ingredientsSection.getKeys(false)) {
                char ingredientChar = key.charAt(0);
                Material ingredientMaterial = Material.matchMaterial(ingredientsSection.getString(key));
                if (ingredientMaterial != null) {
                    recipeIngredients.put(ingredientChar, ingredientMaterial);
                }
            }
        }
    }

    public String getMessage(String key, String... replacements) {
        String message = prefix + messages.getOrDefault(key, "&cСообщение не найдено: " + key);
        for (int i = 0; i < replacements.length; i += 2) {
            message = message.replace("{" + replacements[i] + "}", replacements[i + 1]);
        }
        return ChatColor.translateAlternateColorCodes('&', message);
    }

    public String getFormattedName(HoeLevel level) {
        return ChatColor.translateAlternateColorCodes('&',
                formats.get("name").get(0).replace("{level_name}", level.name()));
    }

    public List<String> getFormattedLore(HoeLevel level, long progress) {
        List<String> loreLines;
        boolean isMaxLevel = getNextLevel(level.id()) == null;

        if (isMaxLevel) {
            loreLines = new ArrayList<>(formats.get("lore_max_level"));
        } else {
            loreLines = new ArrayList<>(formats.get("lore"));
        }

        List<String> customLore = level.lore();
        if (customLore != null && !customLore.isEmpty()) {
            loreLines.addAll(customLore);
        }

        return loreLines.stream()
                .map(line -> ChatColor.translateAlternateColorCodes('&', line
                        .replace("{level_name}", level.name())
                        .replace("{progress}", String.valueOf(progress))
                        .replace("{required}", String.valueOf(level.requiredCrops()))))
                .collect(Collectors.toList());
    }

    public boolean getSetting(String key) {
        return settings.getOrDefault(key, false);
    }

    public HoeLevel getLevel(String id) {
        return levelsById.get(id.toLowerCase());
    }

    public HoeLevel getFirstLevel() {
        return levels.isEmpty() ? null : levels.get(0);
    }

    public HoeLevel getNextLevel(String currentLevelId) {
        if (currentLevelId == null) return null;
        for (int i = 0; i < levels.size() - 1; i++) {
            if (levels.get(i).id().equalsIgnoreCase(currentLevelId)) {
                return levels.get(i + 1);
            }
        }
        return null;
    }

    public List<String> getLevelIds() {
        return levels.stream().map(HoeLevel::id).collect(Collectors.toList());
    }

    public Set<Material> getSupportedCrops() {
        return supportedCrops;
    }

    public boolean isRecipeEnabled() { return recipeEnabled; }
    public List<String> getRecipeShape() { return recipeShape; }
    public Map<Character, Material> getRecipeIngredients() { return recipeIngredients; }

    private String getString(String path, String def) {
        return config.getString(path, def);
    }

    private List<String> getStringList(String path, List<String> def) {
        return config.getStringList(path).isEmpty() ? def : config.getStringList(path);
    }
}
