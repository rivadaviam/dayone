# AWS Accelerator X-Ray Deployment Issue

## Symptom

The AgentCore starter deployment failed while creating the Memory trace
delivery:

```text
AWS::Logs::Delivery | MemoryTracesDelivery
X-Ray Delivery Destination is supported with CloudWatch Logs as a Trace
Segment Destination. Please enable the CloudWatch Logs destination for your
traces using the UpdateTraceSegmentDestination API.
```

CloudFormation then rolled back the `htmx-chatapp-agent` stack.

## Cause

The starter CDK stack configured AgentCore Runtime and Memory trace deliveries
to an `XRAY` destination. That requires the X-Ray trace-segment destination to
be set to `CloudWatchLogs` first.

The original stack attempted to make that change through an account-level
custom resource, but CloudFormation did not guarantee that the custom resource
completed before creating `MemoryTracesDelivery`. This created a deployment
ordering race.

The X-Ray destination setting is scoped to the AWS account and region, not to
an individual IAM user. Enabling it also requires permission to change the
account-level X-Ray configuration. This matters when deploying to a shared
company account.

## Company-account deployment

X-Ray delivery is now opt-in. The normal workshop command is safe for an
account where we are not authorized to change X-Ray configuration:

```bash
cd agentcore/cdk
./deploy-all.sh \
  --region us-east-1 \
  --profile <your-profile> \
  --ingress furl
```

With the default configuration, the deployment keeps application and usage
log delivery but does not create:

- the X-Ray configuration Lambda and custom resource;
- the Runtime or Memory trace delivery sources and deliveries; or
- the X-Ray transaction-search resource policy.

The application and AgentCore Runtime can still be deployed, but X-Ray trace
visualization is not enabled by this mode.

Online evaluation is also skipped in this mode. AgentCore online evaluation
reads trace log groups, so creating an evaluation configuration without trace
delivery produces:

```text
ValidationException: One or more specified log groups do not exist
```

This is expected when the safe mode is used; it is not a separate permission
problem. Online evaluation is created together with X-Ray delivery only when
`--enable-xray-delivery` is supplied.

## Approved sandbox deployment

In an account where account-level X-Ray configuration is approved, enable the
feature explicitly:

```bash
./deploy-all.sh \
  --region us-east-1 \
  --profile <your-profile> \
  --ingress furl \
  --enable-xray-delivery
```

An administrator can also enable the destination separately before deployment:

```bash
aws xray update-trace-segment-destination \
  --destination CloudWatchLogs \
  --region us-east-1

aws xray get-trace-segment-destination \
  --region us-east-1
```

The destination should report `ACTIVE` before trace deliveries are created.

## Related files

- [`accelerator/INTEGRATION_PLAN.md`](../accelerator/INTEGRATION_PLAN.md)
- [`deploy-all.sh`](../agentcore/cdk/deploy-all.sh)
- [`agent-stack.ts`](../agentcore/cdk/lib/agent-stack.ts)
