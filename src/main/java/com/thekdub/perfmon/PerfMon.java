package com.thekdub.perfmon;

import org.bukkit.Bukkit;
import org.bukkit.plugin.Plugin;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.time.Instant;

import com.sun.management.OperatingSystemMXBean;

public class PerfMon extends JavaPlugin {
  
  private final TickMonitor tickMonitor = new TickMonitor(this);
  private final PlayerMonitor playerMonitor = new PlayerMonitor(this);
  private final MemoryMonitor memoryMonitor = new MemoryMonitor(this);
  private final CPUMonitor cpuMonitor = new CPUMonitor(this);
  
  private BukkitTask scribe;
  private final long start = System.currentTimeMillis();
  
  public void onEnable() {
    getDataFolder().mkdirs();
    // Tick Length Tracking for TPS calculation
    tickMonitor.start();
    
    // Player Count Tracking
    playerMonitor.start();
    
    // Resource Usage Tracking
    memoryMonitor.start();
    cpuMonitor.start();
    
    if (!new File(getDataFolder() + File.separator + "data.csv").exists()) {
      try (BufferedWriter writer = new BufferedWriter(
            new FileWriter(
                  new File(getDataFolder() + File.separator + "data.csv")))) {
        writer.write("date_time,uptime_seconds,ticks_per_second,tick_length_ms,player_count," +
              "total_memory,used_memory,free_memory,cpu_usage\n");
        writer.flush();
      } catch (IOException e) {
        e.printStackTrace();
      }
    }
    scribe = Bukkit.getScheduler().runTaskTimerAsynchronously(this, () -> {
      try (BufferedWriter writer = new BufferedWriter(
            new FileWriter(new File(getDataFolder() + File.separator + "data.csv"), true))) {
        writer.write(String.format("%s,%d,%.3f,%.3f,%.3f,%d,%d,%d,%.3f\n",
              Instant.now().toString(),
              (System.currentTimeMillis()-start)/1000,
              tickMonitor.getTPS(),
              tickMonitor.getAvg(),
              playerMonitor.getAvg(),
              memoryMonitor.getMax(),
              memoryMonitor.getUsed(),
              memoryMonitor.getFree(),
              cpuMonitor.getAvg()));
        writer.flush();
      } catch (IOException e) {
        e.printStackTrace();
        scribe.cancel();
      }
    }, 20*60, 20*60*5);
  }
  
  public void onDisable() {
    tickMonitor.stop();
    playerMonitor.stop();
    memoryMonitor.stop();
    cpuMonitor.stop();
    scribe.cancel();
  }
  
  private static abstract class Monitor {
    private final Plugin plugin;
    public double avg = 0;
    public final long avgCount;
    
    private final long frequency;
    private final long delay;
  
    private BukkitTask task = null;
  
    public Monitor(Plugin plugin, long frequency, long delay, long avgCount) {
      this.plugin = plugin;
      this.frequency = frequency;
      this.delay = delay;
      this.avgCount = avgCount;
    }
  
    public void start(Accumulator accumulator) {
      stop();
      task = Bukkit.getScheduler().runTaskTimer(plugin,
            () -> avg = ((avg * (avgCount-1)) + accumulator.run()) / avgCount, delay, frequency);
    }
  
    public void stop() {
      avg = 0;
      if (task != null) {
        task.cancel();
        task = null;
      }
    }
  
    public double getAvg() {
      return avg;
    }
    
    public interface Accumulator {
      double run();
    }
  }
  private static class TickMonitor extends Monitor {
    private long lastTick = 0;
    
    public TickMonitor(Plugin plugin) {
      super(plugin, 1, 1, 20*60);
      lastTick = System.currentTimeMillis();
    }
    
    public void start() {
      lastTick = System.currentTimeMillis();
      super.start(() -> {
        double tmp = System.currentTimeMillis()-lastTick;
        lastTick = System.currentTimeMillis();
        return tmp;
      });
    }
    
    public double getTPS() {
      return 1000.0/Math.max(50.0, avg);
    }
    
  }
  private static class PlayerMonitor extends Monitor {
  
    public PlayerMonitor(Plugin plugin) {
      super(plugin, 20*5, 20*5, 12);
    }
  
    public void start() {
      super.start(() -> Bukkit.getOnlinePlayers().size());
    }
  }
  private static class MemoryMonitor extends Monitor {
    
    public MemoryMonitor(Plugin plugin) {
      super(plugin, 20*5, 20*5, 12);
    }
    
    public void start() {
      super.start(() -> getAllocated() - Runtime.getRuntime().freeMemory());
    }
    
    public long getMax() {
      return Runtime.getRuntime().maxMemory();
    }
    
    public long getAllocated() {
      return Runtime.getRuntime().totalMemory();
    }
    
    public long getFree() {
      return (long) (getMax() - avg);
    }
    
    public long getUsed() {
      return (long) avg;
    }
  }
  private static class CPUMonitor extends Monitor {
    
    public CPUMonitor(Plugin plugin) {
      super(plugin, 20*5, 20*5, 12);
    }
    
    public void start() {
      super.start(() -> ((OperatingSystemMXBean)ManagementFactory.getOperatingSystemMXBean()).getProcessCpuLoad());
    }
  }
}
