**FREE
//==============================================================================
// Program: CPUSTRESS_V2
// Purpose: Enhanced CPU stress test program for IBM i
// Description: Performs intensive calculations to stress CPU cores with
//              improved features: logging, metrics, configurable workload types
// Version: 2.0
// Author: Enhanced by Bob AI Assistant
// Date: 2026-05-06
//==============================================================================

Ctl-Opt DftActGrp(*No) ActGrp(*New) Option(*SrcStmt:*NoDebugIO);

// Program parameters
Dcl-Pi *N;
  pDuration Int(10) Const;      // Duration in seconds
  pWorkloadType Char(10) Const; // MATH, MIXED, HEAVY, LIGHT
  pLogFile Char(50) Const;      // IFS log file path (optional)
End-Pi;

// Global variables
Dcl-S gStartTime Timestamp;
Dcl-S gEndTime Timestamp;
Dcl-S gCurrentTime Timestamp;
Dcl-S gElapsed Int(10);
Dcl-S gIterations Packed(15:0);
Dcl-S gResult Float(8);
Dcl-S gOpsPerSec Packed(15:2);
Dcl-S i Int(10);
Dcl-S j Int(10);
Dcl-S k Int(10);
Dcl-S gLogEnabled Ind Inz(*Off);
Dcl-S gLogMsg Char(256);
Dcl-S gJobName Char(28);

// File for logging
Dcl-F LOGFILE Disk(*Ext) Usage(*Output) Usropn;

// Constants
Dcl-C MAX_CALC_LIGHT 100000;
Dcl-C MAX_CALC_NORMAL 1000000;
Dcl-C MAX_CALC_HEAVY 5000000;
Dcl-C INNER_LOOP_LIGHT 50;
Dcl-C INNER_LOOP_NORMAL 100;
Dcl-C INNER_LOOP_HEAVY 200;

// Data structures
Dcl-Ds JobInfo Qualified;
  JobName Char(10);
  UserName Char(10);
  JobNumber Char(6);
End-Ds;

Dcl-Ds Metrics Qualified;
  TotalIterations Packed(15:0);
  OpsPerSecond Packed(15:2);
  AvgLoopTime Packed(11:6);
  PeakMemory Int(10);
End-Ds;

//==============================================================================
// Main procedure
//==============================================================================

// Initialize
gStartTime = %Timestamp();
gEndTime = gStartTime + %Seconds(pDuration);
gIterations = 0;
Metrics.TotalIterations = 0;

// Get job information
GetJobInfo();

// Setup logging if requested
If pLogFile <> *Blanks;
  SetupLogging();
EndIf;

// Display and log start message
LogMessage('=================================================');
LogMessage('CPU Stress Test V2.0 Started');
LogMessage('Job: ' + %Trim(gJobName));
LogMessage('Duration: ' + %Char(pDuration) + ' seconds');
LogMessage('Workload Type: ' + %Trim(pWorkloadType));
LogMessage('Start Time: ' + %Char(gStartTime));
LogMessage('=================================================');

// Execute workload based on type
Select;
  When %Trim(pWorkloadType) = 'LIGHT';
    ExecuteLightWorkload();
  When %Trim(pWorkloadType) = 'HEAVY';
    ExecuteHeavyWorkload();
  When %Trim(pWorkloadType) = 'MIXED';
    ExecuteMixedWorkload();
  Other;
    ExecuteNormalWorkload();
EndSl;

// Calculate final metrics
CalculateMetrics();

// Display and log results
DisplayResults();

// Cleanup
If gLogEnabled;
  Close LOGFILE;
EndIf;

*InLr = *On;
Return;

//==============================================================================
// Procedures
//==============================================================================

//------------------------------------------------------------------------------
// Get job information
//------------------------------------------------------------------------------
Dcl-Proc GetJobInfo;
  
  Dcl-Pi *N End-Pi;
  
  Dcl-S wJobInfo Char(28);
  
  // Get current job info
  wJobInfo = %Trim(%ScanRpl('/' : ' ' : 
             %Trim(%Subst(%Char(%Job()) : 11 : 28))));
  gJobName = wJobInfo;
  
End-Proc;

//------------------------------------------------------------------------------
// Setup logging
//------------------------------------------------------------------------------
Dcl-Proc SetupLogging;
  
  Dcl-Pi *N End-Pi;
  
  // Note: In production, you would create/open an IFS stream file
  // For this example, we'll use DSPLY for logging
  gLogEnabled = *On;
  
End-Proc;

//------------------------------------------------------------------------------
// Log message
//------------------------------------------------------------------------------
Dcl-Proc LogMessage;
  
  Dcl-Pi *N;
    pMessage Char(256) Const;
  End-Pi;
  
  Dsply (%Trim(pMessage));
  
  // In production, write to IFS file:
  // If gLogEnabled;
  //   Write to stream file
  // EndIf;
  
End-Proc;

//------------------------------------------------------------------------------
// Execute Light Workload
//------------------------------------------------------------------------------
Dcl-Proc ExecuteLightWorkload;
  
  Dcl-Pi *N End-Pi;
  
  Dcl-S wLoopCount Int(10);
  
  LogMessage('Executing LIGHT workload...');
  
  DoW %Timestamp() < gEndTime;
    
    For i = 1 to MAX_CALC_LIGHT;
      
      // Simple mathematical operations
      gResult = %Sqrt(i * 2.5);
      gResult = gResult * gResult;
      
      For j = 1 to INNER_LOOP_LIGHT;
        gResult += (j * 1.5) / (i + 1);
      EndFor;
      
      gIterations += 1;
      
      If %Rem(i:5000) = 0;
        If %Timestamp() >= gEndTime;
          Leave;
        EndIf;
      EndIf;
      
    EndFor;
    
  EndDo;
  
End-Proc;

//------------------------------------------------------------------------------
// Execute Normal Workload (Original)
//------------------------------------------------------------------------------
Dcl-Proc ExecuteNormalWorkload;
  
  Dcl-Pi *N End-Pi;
  
  LogMessage('Executing NORMAL workload...');
  
  DoW %Timestamp() < gEndTime;
    
    For i = 1 to MAX_CALC_NORMAL;
      
      // Mathematical operations
      gResult = %Sqrt(i * 3.14159);
      gResult = gResult * gResult;
      gResult = %Sqrt(gResult) + %Sqrt(i);
      
      // Trigonometric-like calculations
      For j = 1 to INNER_LOOP_NORMAL;
        gResult += (j * 1.732) / (i + 1);
        gResult -= (j * 0.577) * (i + 1);
      EndFor;
      
      // Division operations
      If i > 0;
        gResult = gResult / i;
        gResult = gResult * i;
      EndIf;
      
      gIterations += 1;
      
      If %Rem(i:10000) = 0;
        If %Timestamp() >= gEndTime;
          Leave;
        EndIf;
      EndIf;
      
    EndFor;
    
    // Additional nested loops
    For j = 1 to 1000;
      For k = 1 to 100;
        gResult = %Sqrt(j * k) + (j / (k + 1));
      EndFor;
    EndFor;
    
  EndDo;
  
End-Proc;

//------------------------------------------------------------------------------
// Execute Heavy Workload
//------------------------------------------------------------------------------
Dcl-Proc ExecuteHeavyWorkload;
  
  Dcl-Pi *N End-Pi;
  
  LogMessage('Executing HEAVY workload...');
  
  DoW %Timestamp() < gEndTime;
    
    For i = 1 to MAX_CALC_HEAVY;
      
      // Intensive mathematical operations
      gResult = %Sqrt(i * 3.14159265359);
      gResult = gResult * gResult * gResult;
      gResult = %Sqrt(%Sqrt(gResult)) + %Sqrt(i);
      
      // Heavy trigonometric-like calculations
      For j = 1 to INNER_LOOP_HEAVY;
        gResult += (j * 1.732050808) / (i + 1);
        gResult -= (j * 0.577215665) * (i + 1);
        gResult *= (j * 2.718281828) / (i + 2);
      EndFor;
      
      // Complex division operations
      If i > 0;
        gResult = gResult / i;
        gResult = gResult * i;
        gResult = %Sqrt(gResult) / (i + 1);
      EndIf;
      
      gIterations += 1;
      
      If %Rem(i:20000) = 0;
        If %Timestamp() >= gEndTime;
          Leave;
        EndIf;
      EndIf;
      
    EndFor;
    
    // Heavy nested loops
    For j = 1 to 2000;
      For k = 1 to 200;
        gResult = %Sqrt(j * k) + (j / (k + 1));
        gResult = gResult * %Sqrt(j + k);
      EndFor;
    EndFor;
    
  EndDo;
  
End-Proc;

//------------------------------------------------------------------------------
// Execute Mixed Workload
//------------------------------------------------------------------------------
Dcl-Proc ExecuteMixedWorkload;
  
  Dcl-Pi *N End-Pi;
  
  Dcl-S wCycle Int(10) Inz(0);
  
  LogMessage('Executing MIXED workload...');
  
  DoW %Timestamp() < gEndTime;
    
    wCycle += 1;
    
    // Alternate between light and heavy workloads
    If %Rem(wCycle:2) = 0;
      // Light cycle
      For i = 1 to MAX_CALC_LIGHT;
        gResult = %Sqrt(i * 2.5);
        gIterations += 1;
        If %Timestamp() >= gEndTime;
          Leave;
        EndIf;
      EndFor;
    Else;
      // Heavy cycle
      For i = 1 to MAX_CALC_NORMAL;
        gResult = %Sqrt(i * 3.14159);
        For j = 1 to INNER_LOOP_NORMAL;
          gResult += (j * 1.732) / (i + 1);
        EndFor;
        gIterations += 1;
        If %Timestamp() >= gEndTime;
          Leave;
        EndIf;
      EndFor;
    EndIf;
    
  EndDo;
  
End-Proc;

//------------------------------------------------------------------------------
// Calculate metrics
//------------------------------------------------------------------------------
Dcl-Proc CalculateMetrics;
  
  Dcl-Pi *N End-Pi;
  
  gCurrentTime = %Timestamp();
  gElapsed = %Diff(gCurrentTime:gStartTime:*Seconds);
  
  If gElapsed > 0;
    gOpsPerSec = gIterations / gElapsed;
  Else;
    gOpsPerSec = 0;
  EndIf;
  
  Metrics.TotalIterations = gIterations;
  Metrics.OpsPerSecond = gOpsPerSec;
  
End-Proc;

//------------------------------------------------------------------------------
// Display results
//------------------------------------------------------------------------------
Dcl-Proc DisplayResults;
  
  Dcl-Pi *N End-Pi;
  
  LogMessage('=================================================');
  LogMessage('CPU Stress Test V2.0 Completed');
  LogMessage('End Time: ' + %Char(%Timestamp()));
  LogMessage('Elapsed: ' + %Char(gElapsed) + ' seconds');
  LogMessage('Total Iterations: ' + %Char(gIterations));
  LogMessage('Operations/Second: ' + %Char(gOpsPerSec));
  LogMessage('Final Result: ' + %Char(gResult));
  LogMessage('Workload Type: ' + %Trim(pWorkloadType));
  LogMessage('=================================================');
  
End-Proc;