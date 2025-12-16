===================================================================
--- /dev/null
+++ CPUSTRESS.RPGLE
@@ -0,0 +1,95 @@
+**FREE
+//==============================================================================
+// Program: CPUSTRESS
+// Purpose: CPU stress test program for IBM i
+// Description: Performs intensive calculations to stress CPU cores
+//==============================================================================
+
+Ctl-Opt DftActGrp(*No) ActGrp(*New) Option(*SrcStmt:*NoDebugIO);
+
+// Program parameters
+Dcl-Pi *N;
+  pDuration Int(10) Const;  // Duration in seconds
+  pThreads Int(10) Const;   // Number of threads (1-999)
+End-Pi;
+
+// Global variables
+Dcl-S gStartTime Timestamp;
+Dcl-S gEndTime Timestamp;
+Dcl-S gElapsed Int(10);
+Dcl-S gIterations Packed(15:0);
+Dcl-S gResult Float(8);
+Dcl-S i Int(10);
+Dcl-S j Int(10);
+Dcl-S k Int(10);
+
+// Constants
+Dcl-C MAX_CALC 1000000;
+
+//==============================================================================
+// Main procedure
+//==============================================================================
+
+gStartTime = %Timestamp();
+gEndTime = gStartTime + %Seconds(pDuration);
+gIterations = 0;
+
+// Display start message
+Dsply ('CPU Stress Test Started');
+Dsply ('Duration: ' + %Char(pDuration) + ' seconds');
+Dsply ('Threads: ' + %Char(pThreads));
+
+// Main stress loop
+DoW %Timestamp() < gEndTime;
+  
+  // Perform intensive calculations
+  For i = 1 to MAX_CALC;
+    
+    // Mathematical operations
+    gResult = %Sqrt(i * 3.14159);
+    gResult = gResult * gResult;
+    gResult = %Sqrt(gResult) + %Sqrt(i);
+    
+    // Trigonometric-like calculations (approximation)
+    For j = 1 to 100;
+      gResult += (j * 1.732) / (i + 1);
+      gResult -= (j * 0.577) * (i + 1);
+    EndFor;
+    
+    // Division operations
+    If i > 0;
+      gResult = gResult / i;
+      gResult = gResult * i;
+    EndIf;
+    
+    gIterations += 1;
+    
+    // Check time periodically (every 10000 iterations)
+    If %Rem(i:10000) = 0;
+      If %Timestamp() >= gEndTime;
+        Leave;
+      EndIf;
+    EndIf;
+    
+  EndFor;
+  
+  // Additional nested loops for more CPU stress
+  For j = 1 to 1000;
+    For k = 1 to 100;
+      gResult = %Sqrt(j * k) + (j / (k + 1));
+    EndFor;
+  EndFor;
+  
+EndDo;
+
+// Calculate elapsed time
+gElapsed = %Diff(gEndTime:gStartTime:*Seconds);
+
+// Display results
+Dsply ('CPU Stress Test Completed');
+Dsply ('Elapsed: ' + %Char(gElapsed) + ' seconds');
+Dsply ('Iterations: ' + %Char(gIterations));
+Dsply ('Final Result: ' + %Char(gResult));
+
+*InLr = *On;
+Return;