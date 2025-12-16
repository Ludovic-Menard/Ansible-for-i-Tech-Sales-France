# CPU Stress Test Program - Usage Guide

## Overview
CPUSTRESS is an RPG program designed to stress test CPU resources on IBM i systems. It performs intensive mathematical calculations to generate CPU load for testing and benchmarking purposes.

## Prerequisites
- IBM i V7R2 or higher (for **FREE format RPG)
- Authority to create libraries and programs
- Authority to compile RPG programs

## Installation Steps

### 1. Upload the Source Code
Transfer the `CPUSTRESS.RPGLE` file to your IBM i system using one of these methods:
- FTP
- IFS (Integrated File System)
- IBM i Access Client Solutions (ACS)

### 2. Create a Source Physical File (if needed)
```
CRTSRCPF FILE(YOURLIB/QRPGLESRC) RCDLEN(112)
```

### 3. Copy Source to Source Member
If you uploaded to IFS, copy to a source member:
```
CPYFRMSTMF FROMSTMF('/path/to/CPUSTRESS.RPGLE') 
           TOMBR('/QSYS.LIB/YOURLIB.LIB/QRPGLESRC.FILE/CPUSTRESS.MBR') 
           MBROPT(*REPLACE)
```

### 4. Compile the Program
```
CRTRPGMOD MODULE(YOURLIB/CPUSTRESS) 
          SRCFILE(YOURLIB/QRPGLESRC) 
          SRCMBR(CPUSTRESS) 
          DBGVIEW(*SOURCE)

CRTPGM PGM(YOURLIB/CPUSTRESS) 
       MODULE(YOURLIB/CPUSTRESS) 
       ACTGRP(*NEW)
```

Or use a single command:
```
CRTBNDRPG PGM(YOURLIB/CPUSTRESS) 
          SRCFILE(YOURLIB/QRPGLESRC) 
          SRCMBR(CPUSTRESS) 
          DFTACTGRP(*NO)
```

## Usage

### Basic Syntax
```
CALL PGM(YOURLIB/CPUSTRESS) PARM(duration threads)
```

### Parameters
1. **duration** (Integer): Test duration in seconds
2. **threads** (Integer): Number of concurrent threads (1-999)
   - Note: Single job, but parameter reserved for future multi-threading

### Examples

#### Example 1: 30-second stress test
```
CALL PGM(YOURLIB/CPUSTRESS) PARM(30 1)
```

#### Example 2: 5-minute stress test
```
CALL PGM(YOURLIB/CPUSTRESS) PARM(300 1)
```

#### Example 3: 1-hour stress test
```
CALL PGM(YOURLIB/CPUSTRESS) PARM(3600 1)
```

### Running Multiple Instances
To stress multiple CPU cores, submit multiple jobs:

```
SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(300 1)) JOB(STRESS01)
SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(300 1)) JOB(STRESS02)
SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(300 1)) JOB(STRESS03)
SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(300 1)) JOB(STRESS04)
```

### CL Program to Run Multiple Instances
Create a CL program to automate multiple job submissions:

```
PGM PARM(&DURATION &JOBS)
  DCL VAR(&DURATION) TYPE(*DEC) LEN(10 0)
  DCL VAR(&JOBS) TYPE(*DEC) LEN(5 0)
  DCL VAR(&I) TYPE(*DEC) LEN(5 0)
  DCL VAR(&JOBNAME) TYPE(*CHAR) LEN(10)
  
  CHGVAR VAR(&I) VALUE(1)
  
  DOWHILE COND(&I *LE &JOBS)
    CHGVAR VAR(&JOBNAME) VALUE('STRESS' *CAT %CHAR(&I))
    SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(&DURATION 1)) +
           JOB(&JOBNAME)
    CHGVAR VAR(&I) VALUE(&I + 1)
  ENDDO
  
ENDPGM
```

## Monitoring CPU Usage

### Using WRKACTJOB
```
WRKACTJOB SBS(*ALL) JOB(STRESS*)
```
Press F11 to see CPU percentage.

### Using SQL
```sql
SELECT JOB_NAME, 
       CPU_TIME, 
       ELAPSED_CPU_PERCENTAGE,
       ELAPSED_CPU_TIME
FROM TABLE(QSYS2.ACTIVE_JOB_INFO(
  JOB_NAME_FILTER => 'STRESS*'
)) 
ORDER BY ELAPSED_CPU_PERCENTAGE DESC;
```

### Using Performance Tools
```
WRKSYSSTS
```
Press F11 to cycle through different views including CPU utilization.

## Output
The program displays messages showing:
- Start time and parameters
- Completion status
- Total elapsed time
- Number of iterations completed
- Final calculation result

## Stopping the Program

### Interactive Job
Press F3 or F12 to cancel.

### Batch Job
```
WRKACTJOB JOB(STRESS*)
```
Select option 4 (End) next to the job.

Or use:
```
ENDJOB JOB(jobnumber/username/jobname) OPTION(*IMMED)
```

## Performance Considerations

### CPU Impact
- Each instance will consume close to 100% of one CPU core
- Run as many instances as you have CPU cores for maximum stress
- Monitor system performance to avoid impacting production workloads

### Memory Usage
- Minimal memory footprint per instance
- Safe to run multiple instances

### Disk I/O
- Minimal disk I/O
- Primarily CPU-bound operations

## Best Practices

1. **Test in Non-Production First**: Always test in a development or test environment
2. **Monitor System Resources**: Use WRKSYSSTS or Performance Tools
3. **Set Time Limits**: Use reasonable duration values to prevent runaway processes
4. **Document Tests**: Record CPU utilization before and during tests
5. **Clean Up**: Ensure all test jobs complete or are ended properly

## Troubleshooting

### Program Won't Compile
- Verify IBM i version supports **FREE format (V7R2+)
- Check source member record length (should be 112 or higher)
- Verify authority to create objects

### Low CPU Usage
- Verify job is running: `WRKACTJOB JOB(STRESS*)`
- Check job priority: Lower priority jobs get less CPU time
- Verify system has available CPU capacity

### Job Ends Immediately
- Check joblog: `WRKJOB JOB(jobnumber/username/jobname)` → Option 10
- Verify parameters are valid integers
- Check for authority issues

## Example Test Scenario

### Baseline CPU Test
```
1. Check current CPU: WRKSYSSTS
2. Submit 4 stress jobs:
   SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(600 1)) JOB(STRESS01)
   SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(600 1)) JOB(STRESS02)
   SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(600 1)) JOB(STRESS03)
   SBMJOB CMD(CALL PGM(YOURLIB/CPUSTRESS) PARM(600 1)) JOB(STRESS04)
3. Monitor: WRKACTJOB SBS(*ALL) JOB(STRESS*)
4. Wait for completion (10 minutes)
5. Review results in joblogs
```

## Support
For issues or questions, review the joblog for detailed error messages.

## License
Use at your own risk. This is a stress testing tool and should be used responsibly.