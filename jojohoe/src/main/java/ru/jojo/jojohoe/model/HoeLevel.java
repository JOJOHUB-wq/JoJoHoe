package ru.jojo.jojohoe.model;

import org.bukkit.Material;
import org.bukkit.enchantments.Enchantment;

import java.util.List;
import java.util.Map;

public record HoeLevel(
    String id,
    String name,
    Material material,
    long requiredCrops,
    int fortuneBonus,
    Map<Enchantment, Integer> enchants,
    List<String> lore
) {
}
