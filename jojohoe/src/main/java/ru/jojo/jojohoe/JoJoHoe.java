package ru.jojo.jojohoe;

import com.sk89q.worldguard.WorldGuard;
import com.sk89q.worldguard.protection.flags.StateFlag;
import com.sk89q.worldguard.protection.flags.registry.FlagConflictException;
import com.sk89q.worldguard.protection.flags.registry.FlagRegistry;
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
import ru.jojo.jojohoe.manager.WorldGuardManager;
import ru.jojo.jojohoe.model.HoeLevel;

import java.util.Map;
import java.util.Objects;

public final class JoJoHoe extends JavaPlugin {

    private ConfigManager configManager;
    private HoeManager hoeManager;
    private WorldGuardManager worldGuardManager;
    private NamespacedKey recipeKey;

    public static StateFlag JOJO_HOE_USE_FLAG;

    @Override
    public void onLoad() {
        // Register WorldGuard flag
        FlagRegistry registry = WorldGuard.getInstance().getFlagRegistry();
        try {
            StateFlag flag = new StateFlag("jojo-hoe-use", true);
            registry.register(flag);
            JOJO_HOE_USE_FLAG = flag;
            getLogger().info("Custom WorldGuard flag 'jojo-hoe-use' registered successfully.");
        } catch (FlagConflictException e) {
            getLogger().warning("Could not register WorldGuard flag 'jojo-hoe-use': A flag with that name already exists.");
        }
    }

    @Override
    public void onEnable() {
        this.recipeKey = new NamespacedKey(this, "jojo_hoe_recipe");

        saveDefaultConfig();

        configManager = new ConfigManager(this);
        hoeManager = new HoeManager(this, configManager);

        // Initialize WorldGuard manager if the flag was registered
        if (JOJO_HOE_USE_FLAG != null) {
            worldGuardManager = new WorldGuardManager(JOJO_HOE_USE_FLAG);
        }

        getServer().getPluginManager().registerEvents(new BlockBreakListener(this, configManager, hoeManager), this);

        Objects.requireNonNull(getCommand("hoe")).setExecutor(new HoeCommand(configManager, hoeManager));
        Objects.requireNonNull(getCommand("hoe")).setTabCompleter(new HoeTabCompleter(configManager));

        registerRecipe();

        getLogger().info("JoJoHoe has been enabled!");
    }

    @Override
    public void onDisable() {
        if (Bukkit.getRecipe(recipeKey) != null) {
            Bukkit.removeRecipe(recipeKey);
        }
        getLogger().info("JoJoHoe has been disabled.");
    }

    private void registerRecipe() {
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

    public WorldGuardManager getWorldGuardManager() {
        return worldGuardManager;
    }
}
