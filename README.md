## syncloud

### Summary

This package is motivated by the simple pattern of avoiding complicated IPC by
using consistent file access.  We attempt to generalize this pattern to use S3,
using Python's watchdog library to watch the local directory and publish to S3,
and using AWS's provided S3 Event Notifications to read bucket changes from 
a queue.

### Motivating Example

Norconex Collectors use a Job Execution Framework (JEF) to report status and
collect status. This library makes use of consistent reads and writes to avoid
any complicated IPC and simply use the filesystem.

This keeps the library generic enough that the consultancy behind Norconex Collectors
can apply it in their work.

In a cloud central environment, it needs two pieces to enable distributed functionality
without requiring a network file system such as Amazon EFS:
 * A software which watches an S3 bucket and pulls down changes
 * A software which watches a local directory and publishes to S3.

This project is exactly that.

## syncloud

`syncloud` is the name of the python package inmplemented in this repository, and the command-line
made available by this package. It supports four sub-command(s):

 - setup - Creates an SQS quere and S3 bucket publishing changes to that queue using CloudFormation. This is for informational and testing purposes primarily, as a real use-case would probably involve an operations team doing this.
 - push - watches a directory and pushes files created and modified to an S3 bucket with a prefix
 - pull - watches an S3 bucket and pulls file changes from the S3 bucket

## Configuration

This application will attempt to read its configuration from the following environment variables, 
but also accepts command-line arguements.

## Cloud Orchestration

It may not be appropriate for this library to create/delete the bucket; for very large environments,it may be necessary to insall a Lambda function as an intermediary between the bucket and the queue.

For convenience, this code includes a cloudFormation template, `syncloud/cf/bucket_template.yaml`,
which can be customized for different environments.
