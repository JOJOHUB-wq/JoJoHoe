package ru.jojo.jojohoe.manager;

import com.sk89q.worldedit.bukkit.BukkitAdapter;
import com.sk89q.worldguard.LocalPlayer;
import com.sk89q.worldguard.WorldGuard;
import com.sk89q.worldguard.bukkit.WorldGuardPlugin;
import com.sk89q.worldguard.protection.flags.StateFlag;
import com.sk89q.worldguard.protection.managers.RegionManager;
import com.sk89q.worldguard.protection.regions.RegionContainer;
import org.bukkit.Location;
import org.bukkit.entity.Player;

public class WorldGuardManager {

    private final StateFlag JOJO_HOE_USE_FLAG;

    public WorldGuardManager(StateFlag flag) {
        this.JOJO_HOE_USE_FLAG = flag;
    }

    public boolean canUseHoe(Player player, Location location) {
        RegionContainer container = WorldGuard.getInstance().getPlatform().getRegionContainer();
        RegionManager regions = container.get(BukkitAdapter.adapt(location.getWorld()));

        if (regions == null) {
            // World not managed by WorldGuard, allow by default
            return true;
        }

        LocalPlayer localPlayer = WorldGuardPlugin.inst().wrapPlayer(player);

        // Get the flag value for the applicable regions at the location.
        // DENY takes precedence over ALLOW.
        return regions.getApplicableRegions(BukkitAdapter.adapt(location).toVector().toBlockPoint())
                .queryState(localPlayer, JOJO_HOE_USE_FLAG) != StateFlag.State.DENY;
    }
}
