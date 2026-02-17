# Jira Analysis Guidelines

## Philosophy: Diagnostic, Not Prescriptive

This tool is designed to help identify **WHAT** is wrong, not **HOW** to fix it. The analysis focuses on root cause investigation because the root cause must be confirmed before solutions can be proposed.

## Key Principles

### 1. Focus on Possible Root Causes, Not Solutions

**DO:**
- Identify what the evidence suggests as possible causes
- Present findings as hypotheses that need confirmation
- Use language like "possibly", "likely", "suggests", "indicates"
- Point to specific evidence (log lines, stack traces, error messages)

**DON'T:**
- Provide solutions or fixes
- Suggest immediate actions or workarounds
- Make definitive statements without strong evidence
- Jump to conclusions about how to resolve the issue

**Example - Good:**
```
## Possible Root Causes

Based on the stack trace and error message, this **likely** indicates a 
NetworkOnMainThreadException caused by network I/O on the Android main thread.

Evidence:
- Line 104: "terminating due to uncaught exception of type std::runtime_error: NetworkOnMainThreadException"
- Stack trace shows Call::Cancel() executing on main thread

This **suggests** that the cancel operation is performing synchronous network 
operations that Android's StrictMode is blocking.
```

**Example - Bad:**
```
## Root Cause

This is definitely a NetworkOnMainThreadException. 

## Recommendations

1. Move the network call to a background thread
2. Add try-catch around the cancel operation
3. Disable StrictMode in production
```

### 2. Filter Bot Comments Automatically

Bot comments (like auto-triage messages from `svc_kaizen_atlassian`) add noise and are not relevant to technical analysis. The tool automatically filters these out.

**Filtered by default:**
- `svc_kaizen_atlassian` - Auto-triage bot
- `svc_jiradel_svc` - Jira delivery service
- `svc_navsdk_jira` - NavSDK automation
- Any account starting with `svc_`
- Accounts containing "automation" or "bot"

**Customizable:**
You can add more bot usernames in your `config.yaml`:

```yaml
ignore_bot_users:
  - "svc_kaizen_atlassian"
  - "my_custom_bot"
  - "another_automation_account"
```

### 3. Emphasize Investigation Steps, Not Solutions

The "Recommendations" section has been renamed to **"Next Steps for Investigation"** to focus on:

**What to include:**
- Verification steps to confirm the suspected root cause
- Additional data or logs that would help
- Diagnostic steps to reproduce or isolate the issue
- What to monitor or measure

**What to avoid:**
- Quick fixes or workarounds
- Implementation details of solutions
- Long-term architectural changes
- Code changes or patches

**Example - Good:**
```
## Next Steps for Investigation

### Verify Root Cause
1. Check if StrictMode is enabled in the app's debug build
2. Confirm that Call::Cancel() performs network I/O by reviewing the framework-http code
3. Verify if the issue reproduces when ProtobufBasedHttpMiddlewareFeature is disabled

### Additional Data Needed
1. Logs from a Debug build to see if issue persists
2. Network traces during the cancel operation
3. Thread dumps showing which thread invokes the cancel
```

**Example - Bad:**
```
## Recommendations

### Immediate Actions
1. Wrap Call::Cancel() in try-catch to handle the exception
2. Move the cancel operation to a background executor

### Long-term Solutions
1. Refactor the HTTP framework to make cancel operations async
2. Add thread safety checks in CI/CD
```

## Analysis Structure

The analysis follows this structure:

1. **📋 Summary** - Brief overview of the issue (symptoms, impact, priority)

2. **🔍 Possible Root Causes** - Evidence-based hypotheses about what's wrong
   - NOT definitive statements
   - NOT how to fix it
   - Supported by specific evidence (log lines, errors, stack traces)

3. **📊 Patterns & Observations** - Recurring patterns, timing issues, anomalies

4. **🔧 Technical Details** - Error messages, stack traces, system state

5. **💡 Next Steps for Investigation** - What to verify, what data to collect, how to diagnose
   - NOT solutions or fixes
   - Focus on confirming the root cause

6. **⚠️ Risk Assessment** - Severity, likelihood, business impact

## Language Guidelines

### Use Uncertainty Language

Since root causes aren't confirmed, use appropriate hedging:

| Instead of | Use |
|------------|-----|
| "The issue is..." | "The evidence suggests..." |
| "This is caused by..." | "This is likely caused by..." |
| "The root cause is..." | "The possible root cause is..." |
| "This will fix it" | "To confirm this hypothesis..." |
| "The problem is X" | "This pattern indicates X" |

### Be Evidence-Based

Always tie findings to evidence:

✅ **Good:**
- "Line 142 shows the exception thrown in stop_callback::execute()"
- "The stack trace indicates the call originates from the main thread"
- "Three separate log entries show the same timeout pattern"

❌ **Bad:**
- "This is probably a threading issue"
- "It seems like a race condition"
- "I think the network is slow"

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Jumping to Solutions

**Wrong:**
```
The app crashes due to NetworkOnMainThreadException. 
Fix: Move the network call to a background thread.
```

**Right:**
```
The crash log indicates a NetworkOnMainThreadException. This suggests 
that network I/O is being performed on the main thread. To confirm:
1. Verify which code path triggers the network operation
2. Check if the call is synchronous or has a blocking wait
```

### ❌ Pitfall 2: Being Too Definitive

**Wrong:**
```
## Root Cause

The root cause is that Call::Cancel() blocks the main thread.
```

**Right:**
```
## Possible Root Causes

Based on the exception and stack trace, this likely indicates that 
Call::Cancel() performs network I/O synchronously on the main thread.
Evidence:
- Exception type: NetworkOnMainThreadException
- Stack trace shows cancel invoked on main thread (frame #11)

This hypothesis should be confirmed by reviewing the Call::Cancel() implementation.
```

### ❌ Pitfall 3: Including Bot Commentary

**Wrong:**
```
## Comments

Comment 1 - svc_kaizen_atlassian:
"Auto-triaged to team X based on component Y"

Comment 2 - John Developer:
"I can reproduce this issue"
```

**Right:**
```
## Comments

Comment 1 - John Developer:
"I can reproduce this issue"

[Bot comments automatically filtered]
```

### ❌ Pitfall 4: Prescriptive Recommendations

**Wrong:**
```
## Recommendations

1. Add try-catch around the stop_callback
2. Implement async cancellation in framework-http
3. Enable stricter threading checks in debug builds
```

**Right:**
```
## Next Steps for Investigation

### Verify the Hypothesis
1. Confirm that Call::Cancel() performs network I/O by code review
2. Test if disabling ProtobufBasedHttpMiddlewareFeature prevents the crash
3. Check if Debug builds exhibit the same behavior

### Additional Data Needed
1. Thread dumps showing execution context
2. Framework-http change log around June 5th
3. Network traces during cancel operations
```

## Benefits of This Approach

1. **More Accurate** - Avoids suggesting fixes for unconfirmed causes
2. **More Useful** - Focuses investigation efforts on validation
3. **Less Noise** - Filters out irrelevant bot comments
4. **Better Signal** - Emphasizes evidence over speculation
5. **Clearer** - Explicit about uncertainty and what needs confirmation

## Configuration Example

```yaml
# config.yaml

# Focus analysis on these keywords
keywords:
  - "error"
  - "exception"
  - "crash"
  - "timeout"

# Filter bot comments
ignore_bot_users:
  - "svc_kaizen_atlassian"
  - "svc_jiradel_svc"
  - "svc_navsdk_jira"
  - "automation"
  - "bot"
  - "svc_"  # Any service account

# Analysis settings
analysis_depth: "deep"
max_log_lines: 500
context_lines: 5
```

## Summary

- **Diagnostic, not prescriptive** - Identify what's wrong, not how to fix it
- **Hypotheses, not certainties** - Use uncertainty language appropriately
- **Evidence-based** - Always tie findings to specific evidence
- **Investigation-focused** - Next steps should verify and confirm
- **Noise-free** - Automatically filter bot comments
- **Clear structure** - Follow the 6-section analysis framework

The goal is to provide a clear, evidence-based analysis that helps confirm the root cause before jumping to solutions.
