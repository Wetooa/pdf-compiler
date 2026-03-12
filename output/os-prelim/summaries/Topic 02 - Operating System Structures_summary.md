# Learning Guide: Topic 02 - Operating System Structures.pdf


*Generated on 2026-03-12 20:00:58*


*This is a simplified learning guide created from the original PDF. Use this for studying instead of reading the lengthy original text.*


---


## Pages 1-20


Here is a simplified, easy-to-read learning guide based on the provided text, designed for study purposes.

---

## Operating System Structures & Shell Scripting

**Course:** CS348
**Topic:** Operating System Structures & Shell Scripting

---

### Intended Learning Outcomes (ILOs)

Upon completing this topic, you should be able to:
1.  Identify different system components.
2.  List the OS responsibilities for system components.
3.  Describe OS services.
4.  Manipulate Linux commands using shell scripting.
5.  Explain the system boot process.
6.  Explain process concepts, states, and characteristics.

---

### 1. User and Operating System Interface

Almost all Operating Systems (OS) have a User Interface (UI).

#### 1.1 Types of User Interfaces:
*   **Command Line Interface (CLI)**: Also known as a command interpreter (CI). Users type commands directly.
*   **Graphical User Interface (GUI)**: User-friendly interface with visual elements (icons, windows) and dedicated I/O devices (mouse, keyboard).
*   **Batch**: Commands are placed in a file, and then the file is executed.

#### 1.2 Command Line Interface (CLI) / Command Interpreter (CI) Details:
*   **Shells**: On systems with multiple CIs, they are called Shells (e.g., Bash, CSH).
*   **Shell Scripts**: A sequence of command-line steps saved in a file, which can be run like a program.
*   **Common CLI commands** are for file manipulation (e.g., Create, Delete, List, Print, Copy, Execute).

#### 1.3 CLI Command Execution Approaches:
1.  **Interpreter Implements Commands**: The code for the command (e.g., `cd` for `change directory` in Windows) is built directly into the interpreter.
2.  **Program Implements Commands**: The command (e.g., `rm` for `remove` in UNIX) is a separate program file. The interpreter executes this program.

---

### 2. System Calls

A **System Call** is how programs request services from the operating system.

#### 2.1 Key Components:
*   **Application Programming Interface (API)**: A set of functions available to application programmers.
    *   Examples: Windows API, POSIX API (for UNIX, Linux, MacOSX), Java API.
*   **System Call Interface**: A layer that links API function calls to the necessary OS system calls. It intercepts API calls and invokes corresponding system calls (often via a table).

#### 2.2 System Call Flow (User Mode to Kernel Mode):
1.  A program in **User Mode** calls an API function (e.g., `open()`).
2.  The System Call Interface intercepts this call.
3.  The CPU switches to **Kernel Mode** (a privileged mode where the OS runs).
4.  The OS executes the system call's implementation (e.g., `open()` system call).
5.  The CPU switches back to User Mode, and the result is returned to the program.

#### 2.3 Methods for Passing Parameters to the OS during System Calls:
*   **Via Registers**: Parameters are stored in CPU registers. Limited by the number of available registers.
*   **Via Address (Memory Block)**: Parameters are stored in a memory block, and the memory address of this block is passed via a register.
*   **Via Stack**: Parameters are pushed onto the program's process stack, and the OS pops them off.

#### 2.4 Types of System Calls:
1.  **Process Control**: Manage processes (create, terminate, synchronize).
    *   Examples: `fork()` (create a new process), `exit()` (terminate current process).
2.  **File Manipulation**: Handle file operations (create, read, write, delete).
    *   Examples: `open()`, `read()`, `write()`.
3.  **Device Manipulation**: Manage hardware device interactions (printers, disks).
    *   Examples: `ioctl()` (device control), `read()`, `write()`.
4.  **Information Maintenance**: Retrieve and modify system data (time, process details, configuration).
    *   Examples: `getpid()` (get process ID), `settimeofday()` (set system time).
5.  **Communication**: Enable inter-process communication (IPC) via message passing or shared memory.
    *   Examples: `pipe()`, `socket()`.
6.  **Protection**: Control resource access and enforce security policies.
    *   Examples: `chmod()` (change file permissions), `setuid()` (set user ID).

---

### 3. Linux Shell Commands & Scripts

*   **Requirement**: A Linux system (e.g., via Virtual Machine) is needed for practical work.
*   **Virtual Machine (VM)**: A virtual computer system that runs on top of a physical machine.

#### 3.1 Hypervisor (Virtual Machine Monitor / VMM):
*   A program that creates and runs virtual machines.
*   **Type I Hypervisor (Bare-metal)**: Runs directly on hardware, acting like a lightweight OS (e.g., VMware ESXi).
*   **Type II Hypervisor (Hosted)**: Runs as an application on top of an existing host OS (e.g., VirtualBox, VMware Workstation). It borrows resources from the host.

#### 3.2 The Shell:
*   **Definition**: The outermost layer of the OS, a special user program that provides an interface for users to access OS services.
*   **Shell Scripts**: Files containing commands that the shell executes, used for automation.
*   **Common Linux Shells**:
    *   **BASH** (Bourne Again SHell) - Most common default.
    *   **CSH** (C SHell)
    *   **KSH** (Korn SHell)

---

### 4. Working with CLI/CI (Linux)

#### 4.1 Command Prompt Indicators:
*   `$`: Indicates the current user is a **normal user**.
*   `#`: Indicates the current user is a **root user** (superuser).

#### 4.2 User and Hostname Indicator:
*   `username@hostname`: Shows the current user and the machine's name.

#### 4.3 Special Directories:
*   `~`: Represents the **user's home directory** (e.g., `/home/<username>/`).
*   `/`: Represents the **root directory** (the top-level directory of the file system).

#### 4.4 Normal User vs. Root User:

| Normal User                                     | Root User (Superuser)                               |
| :---------------------------------------------- | :-------------------------------------------------- |
| Access and modify files in their own home (`/home/username/`). | **Unrestricted access** to all system resources.    |
| Run software that doesn't require system-wide changes. | Ability to modify **critical system files**.        |
| Change only their own password.                 | Can change any password, including other users'.    |
| Create, modify, delete files *only* within their home directory. | Can create, modify, delete files anywhere on the system. |
| Can use `sudo` (if allowed) to run specific commands with admin rights. | Inherently has admin rights.                        |

#### 4.5 Checking Current User:
*   `whoami`: Prints the current user's username.
    ```bash
    mario@host~$ whoami
    mario
    root@host~# whoami
    root
    ```
*   `id -u`: Prints the current user's User ID (UID).
    *   **Root user's UID is always `0`**.
    ```bash
    mario@host~$ id -u
    1000
    root@host~# id -u
    0
    ```

#### 4.6 Identifying and Changing Your Shell:
*   `which $SHELL`: Shows the path to your current default shell. (Useful for scripting).
    ```bash
    $ which $SHELL
    /bin/bash
    ```
*   `chsh`: Change your login shell. You will be prompted to enter the path to the new shell.
*   `chsh -s /bin/bash`: Directly specifies `/bin/bash` as your new shell.
    *   *(Note: Changes usually take effect after logging out and logging back in.)*

---


---


## Pages 19-38


Here is a simplified, easy-to-read learning guide based on the provided text:

---

# Linux Command Line Learning Guide

## 1. User & Shell Information

### Checking Current User
-   **`whoami`**: Displays the current user's username.
    *   *Example:* `mario`
-   **`id -u`**: Displays the current user's User ID (UID).
    *   *Note:* The root user's ID is always `0`.
    *   *Example:* `1000` (for a regular user), `0` (for root)

### Identifying & Changing Shell
-   **`which $SHELL`**: Shows the full path of your current shell (e.g., `/bin/bash`).
-   **Changing Your Default Shell:**
    *   **`chsh`**: Prompts you to change your login shell.
    *   **`chsh -s /bin/bash`**: Directly sets your default shell to Bash.

## 2. File and Directory Management

### Navigating & Listing
-   **`pwd`** (Print Working Directory): Displays the absolute path of your current directory.
-   **`ls`** (List): Displays files and directories in the current location.
    *   **Common Options:**
        *   **`-l`**: Long format, showing detailed information (permissions, owner, size, date).
        *   **`-a`**: Show all files, including hidden ones (which start with a `.`).
        *   **`-h`**: Human-readable file sizes (e.g., `11K`, `2M`).
        *   **`-R`**: Recursive, lists contents of subdirectories.
    *   **Combine Options:** `ls -lah` (long, all, human-readable).

### Understanding `ls -l` Output
*Example Output:* `-rwxrw-r-- 3 testuser usergroup 11K Feb 14 19:30 file.txt`
1.  **File Type & Permissions (`-rwxrw-r--`)**:
    *   First character: `-` for a regular file, `d` for a directory.
    *   Next nine characters: Permissions for **owner** (first three), **group** (middle three), and **others** (last three).
        *   `r`: read permission
        *   `w`: write permission
        *   `x`: execute permission
        *   `-`: no permission
2.  **Hard Links (`3`)**: Number of direct links to the file/directory.
3.  **Owner (`testuser`)**: The user who owns the file/directory.
4.  **Group (`usergroup`)**: The group that owns the file/directory.
5.  **File Size (`11K`)**: Size of the file (human-readable if `-h` is used).
6.  **Date Modified (`Feb 14 19:30`)**: Last modification date and time.
7.  **File Name (`file.txt`)**: The name of the file or directory.

### Creating & Deleting
-   **`cd <directory>`** (Change Directory): Moves your current working directory.
    *   **`cd ~`**: Go to your home directory.
    *   **`cd /`**: Go to the root directory.
    *   **`cd ..`**: Go up one level to the parent directory.
-   **`mkdir <my_folder>`** (Make Directory): Creates a new directory.
    *   **`-p`**: Creates parent directories as needed (e.g., `mkdir -p a/b/c` will create `a`, then `b` inside `a`, then `c` inside `b`).
-   **`rmdir <my_folder>`** (Remove Directory): Deletes an **empty** directory.
-   **`rm <file_or_dir>`** (Remove): Deletes files or directories.
    *   **Common Options:**
        *   **`-r`** (Recursive): Required to delete directories and their contents.
        *   **`-f`** (Force): Deletes without confirmation. **Use with caution!**
        *   **`-i`** (Interactive): Prompts for confirmation before each deletion.
        *   **`-v`** (Verbose): Shows details of deleted files.

### Copying & Moving
-   **`cp <source> <destination>`** (Copy): Copies files or directories.
    *   **Common Options:**
        *   **`-r`** (Recursive): Required to copy directories and their contents.
        *   **`-i`** (Interactive): Prompts before overwriting an existing file.
        *   **`-u`** (Update): Copies only if the source is newer than the destination, or if the destination file doesn't exist.
        *   **`-v`** (Verbose): Shows progress of copying.
-   **`mv <source> <destination>`** (Move / Rename): Moves files/directories or renames them.
    *   **Common Options:**
        *   **`-i`** (Interactive): Prompts before overwriting.
        *   **`-u`** (Update): Moves only if the source is newer than the destination, or if the destination file doesn't exist.
        *   **`-v`** (Verbose): Shows progress.

## 3. File Viewing and Editing

### Viewing File Contents
-   **`cat <file.txt>`** (Concatenate and Print): Displays the entire contents of a file to the screen.
-   **`less <file.txt>`**: Displays file contents page by page, allowing scrolling.
    *   **Navigation:**
        *   `SPACEBAR`: Scroll down one page.
        *   `b`: Scroll up one page.
        *   `/keyword`: Search for a specific keyword.
        *   `q`: Quit `less`.

### Editing Files
-   **`nano <file.txt>`**: Opens the file in the Nano text editor.
    *   **Shortcuts:**
        *   `CTRL-X`: Exit (prompts to save if changes were made).
        *   `CTRL-O`: Save changes.
        *   `CTRL-W`: Search for text.

## 4. File Permissions & Ownership

### Modifying File Permissions (`chmod`)
-   **`chmod <permissions> <file>`**: Changes the read, write, and execute permissions of a file or directory.
    *   **Symbolic Mode:**
        *   `chmod +w script.sh`: Adds write permission.
        *   `chmod -w script.sh`: Removes write permission.
        *   `u/g/o/a`: User (owner), Group, Others, All.
        *   `+/-/=`: Add, Remove, Set permissions.
        *   `r/w/x`: Read, Write, Execute.
        *   *Example:* `chmod u+x script.sh` (add execute for owner).
    *   **Octal (Numeric) Mode:** Uses three digits (0-7), representing permissions for **Owner**, **Group**, and **Others**.
        *   **Values:**
            *   `4` = Read (`r`)
            *   `2` = Write (`w`)
            *   `1` = Execute (`x`)
            *   **Combinations:** `7` = `rwx` (4+2+1), `6` = `rw-` (4+2), `5` = `r-x` (4+1), `4` = `r--` (4).
        *   *Example:* `chmod 755 script.sh`
            *   `7` (owner): `rwx`
            *   `5` (group): `r-x`
            *   `5` (others): `r-x`

### Changing File Ownership (`chown`)
-   **`chown <user>:<group> <file.txt>`**: Changes the owner and/or group of a file or directory.
    *   *Example:* `chown newuser:newgroup file.txt`
    *   *Example:* `chown newuser file.txt` (changes owner only)
    *   *Example:* `chown :newgroup file.txt` (changes group only)

## 5. Process Management

### Monitoring Processes
-   **`ps aux`**: Lists all active processes for all users, showing detailed information.
    *   **`a`**: Show processes for all users.
    *   **`u`**: Show detailed user-oriented format.
    *   **`x`**: Show processes not attached to a terminal.
-   **`top`**: Displays a real-time, dynamic view of running processes and system resource usage (CPU, memory).
    *   **Navigation within `top`:**
        *   `q`: Quit `top`.
        *   `k`: Kill a process (prompts for PID).
        *   `M`: Sort processes by memory usage.

### Terminating Processes (`kill`)
-   **`kill <PID>`**: Sends a signal to terminate a process specified by its Process ID (PID).
    *   **Common Signals:**
        *   **`-9`** (SIGKILL): Forces immediate termination; cannot be caught or ignored by the process. Use as a last resort.
        *   **`-15`** (SIGTERM): Graceful termination request; allows the process to clean up before exiting. This is the default and preferred method.

## 6. Shell Scripting Fundamentals

A **Shell Script** is a text file containing a series of commands executed sequentially by a shell interpreter.

### Essential Components of a Shell Script

1.  **Shebang (`#!`)**:
    *   The very first line of a script.
    *   Specifies the interpreter to use for running the script (e.g., `#!/bin/bash`).
    *   *Importance:* Ensures the script executes with the intended shell.

2.  **Comments (`#`)**:
    *   Lines starting with `#` (except the shebang) are ignored by the shell.
    *   Used to add explanations, notes, or temporarily disable code.
    *   *Example:* `# This is a comment explaining the next command.`

3.  **Commands**:
    *   Standard Unix/Linux commands (e.g., `echo`, `ls`, `mkdir`).
    *   Executed in order from top to bottom.
    *   *Example:* `echo "Hello, World!"`

4.  **Variables**:
    *   Used to store data.
    *   **Assignment**: `variable_name="value"`
        *   **Important:** No spaces around the `=` sign during assignment.
        *   *Example:* `name="Jefferson"` (Correct) vs. `name = "Jefferson"` (Incorrect)
    *   **Accessing Value**: Use a `$` before the variable name (e.g., `echo "Hello, $name!"`).

5.  **Input and Output**:
    *   **Output**:
        *   `echo <text>`: Prints text or variable values to the standard output.
    *   **Input**:
        *   `read <variable_name>`: Reads a line of input from the user and stores it in the specified variable.
        *   *Example:*
            ```bash
            echo "Enter your name:"
            read user_name
            echo "Hello, $user_name!"
            ```

6.  **Control Statements**:
    *   **Purpose**: Control the flow of execution based on conditions or for repeating tasks.
    *   **Syntax & Spacing**: Keywords like `if`, `then`, `else`, `fi`, `for`, `do`, `done`, `while` typically require new lines. A semicolon `;` can be used to separate commands on a single line.
    *   **Condition Checking**:
        *   Can use the `test` command or square brackets `[ ]`.
        *   *Important:* Spaces are critical inside `[ ]` (e.g., `[ "$name" == "Jefferson" ]`).
        *   **Examples**: `test "$name" == "Jefferson"` or `[ "$name" == "Jefferson" ]`

    *   **Comparison Operations (Numbers)**: Used within `[ ]` or `test`.
        *   `-eq`: Equal to
        *   `-ne`: Not equal to
        *   `-gt`: Greater than
        *   `-lt`: Less than
        *   `-ge`: Greater than or equal to
        *   `-le`: Less than or equal to

    *   **Comparison Operations (Strings)**: Used within `[ ]` or `test`.
        *   `=`: Equal to
        *   `!=`: Not equal to

    *   **If-Else Statement**:
        ```bash
        if [ "$name" == "Jefferson" ]; then
            echo "Welcome, $name!"
        else
            echo "Access Denied!"
        fi
        ```

    *   **For Loop**: Iterates over a list of items.
        ```bash
        for i in {1..5}; do
            echo "Iteration $i"
        done
        ```

    *   **While Loop**: Executes commands as long as a condition is true.
        ```bash
        count=1
        while [ "$count" -le 5 ]
        do
            echo "Count: $count"
            count=$((count + 1)) # Increment count
        done
        ```

7.  **Functions**:
    *   Blocks of code that can be called by name.
    *   **Definition**:
        ```bash
        greet() {
            echo "Hello, $1!"
        }
        ```
    *   **Calling**: `greet "Jefferson"`
    *   **Arguments**: `$1`, `$2`, etc., refer to the arguments passed to the function.

8.  **Exit Status (`$?`)**:
    *   `echo $?`: Prints the exit status of the *most recently executed command*.
    *   `0`: Indicates successful execution.
    *   Non-zero value (e.g., `1`, `2`): Indicates an error or failure.
    *   *Example:*
        ```bash
        mkdir test_dir # This command creates a directory
        echo "Exit status: $?" # Prints 0 if mkdir was successful
        ```
---


---


## Pages 37-40


Here is a simplified, easy-to-read learning guide based on the provided text:

---

## Shell Scripting Essentials: A Learning Guide

This guide covers fundamental concepts and components of shell scripting.

### 1. What is a Shell Script?

*   A shell script is a **text file** containing a series of commands.
*   These commands are **executed sequentially** by a **shell interpreter** (e.g., Bash).

### 2. Basic Script Structure

*   **Shebang:** The very first line in a script, `#!/bin/bash`, tells the system which interpreter to use (in this case, Bash).
*   **Comments:** Lines starting with `#` are ignored by the interpreter. They are used for explanations.
    ```bash
    #!/bin/bash
    # This is a comment explaining the script's purpose
    ```
*   **Basic Output:** The `echo` command prints text to the terminal.
    ```bash
    echo "Hello, World!"
    echo "Listing files:"
    ls -l
    ```

### 3. Variables

*   **Definition:** Variables store data.
*   **Assignment:** Assign a value using `name="value"` (no spaces around `=`).
*   **Usage (Expansion):** Access the variable's value by prefixing its name with `$`.
    ```bash
    name="Jefferson"
    echo "Hello, $name!" # Output: Hello, Jefferson!
    ```

### 4. Input and Output

*   **Output (echo):** As seen above, `echo` displays information.
*   **Input (read):** The `read` command waits for user input from the keyboard and stores it in a specified variable.
    ```bash
    echo "Enter your name:"
    read user_name
    echo "Hello, $user_name!"
    ```

### 5. Control Statements (Conditional Logic & Loops)

Control statements allow scripts to make decisions and repeat actions.

#### A. Comparison Operations

Used in conditional statements to compare values.

*   **Numbers:**
    *   `-eq`: equal to
    *   `-ne`: not equal to
    *   `-gt`: greater than
    *   `-lt`: less than
    *   `-ge`: greater than or equal to
    *   `-le`: less than or equal to
*   **Strings:**
    *   `=`: equal to
    *   `!=`: not equal to

#### B. `if`/`else` (Conditional Execution)

Executes different blocks of code based on a condition.
*   Conditions are typically enclosed in `[ ]` or `[[ ]]`.
*   `then` starts the block for a true condition.
*   `else` starts the block for a false condition.
*   `fi` ends the `if` statement.

```bash
if [ "$name" == "Jefferson" ]; then
  echo "Welcome, $name!"
else
  echo "Access Denied!"
fi
```

#### C. `for` Loop (Iteration)

Repeats a block of code for each item in a list or a range.
*   `do` starts the loop body.
*   `done` ends the loop.

```bash
for i in {1..5}; do # Loop from 1 to 5
  echo "Iteration $i"
done
```

#### D. `while` Loop (Conditional Iteration)

Repeats a block of code as long as a condition remains true.
*   `do` starts the loop body.
*   `done` ends the loop.
*   **Arithmetic Expansion (`$(( ))`):** Used for mathematical calculations within the script.
    ```bash
    count=1
    while [ "$count" -le 5 ]; do
      echo "Count: $count"
      count=$((count + 1)) # Increment count
    done
    ```

### 6. Functions

*   **Purpose:** Organize reusable blocks of code, making scripts modular and easier to manage.
*   **Definition:** Define a function with `function_name() { ... }`.
*   **Arguments:**
    *   `$1`, `$2`, etc., represent the arguments passed to the function when it's called. `$1` is the first argument, `$2` the second, and so on.
*   **Syntax:** The opening brace `{`, function body, and closing brace `}` are typically on separate lines.

```bash
greet() {
  echo "Hello, $1!" # $1 refers to the first argument passed
}

greet "Jefferson" # Calls the function, passing "Jefferson" as $1
```

### 7. Exit Status

*   **Purpose:** Every command or script returns an "exit status" (an integer) upon completion. This indicates whether the command succeeded or failed.
*   **Value:**
    *   `0`: Indicates success.
    *   Non-zero (e.g., `1`, `2`): Indicates an error or failure.
*   **Access:** The special variable `$?` holds the exit status of the *last executed command*.

```bash
mkdir test_dir        # Try to create a directory
echo "Exit status: $?" # Prints 0 if successful, non-zero if it failed (e.g., dir already exists)
```

### 8. Expansion Operators (`$`)

The `$` symbol is used for various types of "expansion" where a symbol or expression is replaced by its value.

*   `$name`: **Variable Expansion** – Returns the value of the variable `name`.
*   `$()`: **Command Expansion** – Executes the command inside the parentheses and substitutes its output.
    *   Example: `echo "Current date: $(date)"`
*   `$(())`: **Arithmetic Expansion** – Performs arithmetic calculations.
    *   Example: `result=$((5 + 5))`
*   `$$`: **PID of Current Shell** – Returns the Process ID of the shell running the script.
*   `$?`: **Exit Status** – Returns the exit status of the last executed command.
*   `$1`, `$2`, ...: **Positional Arguments** – Within a script or function, these refer to the arguments passed to it (e.g., `script.sh arg1 arg2` would have `$1="arg1"` and `$2="arg2"`).

---


---
