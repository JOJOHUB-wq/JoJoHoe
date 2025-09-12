package ru.jojo.jojohoe;

import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.ShapedRecipe;
import org.bukkit.plugin.java.JavaPlugin;
import ru.jojo.jojohoe.command.HoeCommand;
import ru.jojo.jojohoe.command.HoeTabCompleter;
import ru.jojo.jojohoe.listener.BlockBreakListener;
import ru.jojo.jojohoe.manager.ConfigManager;
import ru.jojo.jojohoe.manager.HoeManager;
import ru.jojo.jojohoe.model.HoeLevel;

import java.util.Map;
import java.util.Objects;

public final class JoJoHoe extends JavaPlugin {

    private ConfigManager configManager;
    private HoeManager hoeManager;
    private NamespacedKey recipeKey;


    @Override
    public void onEnable() {
        this.recipeKey = new NamespacedKey(this, "jojo_hoe_recipe");

        saveDefaultConfig();

        configManager = new ConfigManager(this);
        hoeManager = new HoeManager(this, configManager);

        getServer().getPluginManager().registerEvents(new BlockBreakListener(configManager, hoeManager), this);

        Objects.requireNonNull(getCommand("hoe")).setExecutor(new HoeCommand(configManager, hoeManager));
        Objects.requireNonNull(getCommand("hoe")).setTabCompleter(new HoeTabCompleter(configManager));

        registerRecipe();

        getLogger().info("JoJoHoe has been enabled!");
    }

    @Override
    public void onDisable() {
        // Unregister recipe on disable to support reloads
        if (Bukkit.getRecipe(recipeKey) != null) {
            Bukkit.removeRecipe(recipeKey);
        }
        getLogger().info("JoJoHoe has been disabled.");
    }

    private void registerRecipe() {
        // Clean up old recipe before registering new one, for reloads
        if (Bukkit.getRecipe(recipeKey) != null) {
            Bukkit.removeRecipe(recipeKey);
        }

        if (!configManager.isRecipeEnabled()) {
            return;
        }

        HoeLevel firstLevel = configManager.getFirstLevel();
        if (firstLevel == null) {
            getLogger().warning("Recipe is enabled, but no levels are defined. Cannot create recipe.");
            return;
        }

        ItemStack resultHoe = hoeManager.createHoe(firstLevel.id());
        if (resultHoe == null) {
            getLogger().warning("Failed to create result item for recipe.");
            return;
        }

        ShapedRecipe recipe = new ShapedRecipe(recipeKey, resultHoe);

        String[] shape = configManager.getRecipeShape().toArray(new String[0]);
        if (shape.length == 0) {
            getLogger().warning("Recipe is enabled, but shape is not defined correctly.");
            return;
        }
        recipe.shape(shape);

        Map<Character, Material> ingredients = configManager.getRecipeIngredients();
        if (ingredients.isEmpty()) {
            getLogger().warning("Recipe is enabled, but no ingredients are defined.");
            return;
        }

        for (Map.Entry<Character, Material> entry : ingredients.entrySet()) {
            recipe.setIngredient(entry.getKey(), entry.getValue());
        }

        Bukkit.addRecipe(recipe);
        getLogger().info("Custom hoe recipe has been registered.");
    }

    public ConfigManager getConfigManager() {
        return configManager;
    }

    public HoeManager getHoeManager() {
        return hoeManager;
    }
}
