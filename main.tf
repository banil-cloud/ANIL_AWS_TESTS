provider "aws" {
  region = "us-east-1"
}

# 1. IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# 2. Attach policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3. Package the Python code into a zip file (locally before applying)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

# 4. Lambda Function
resource "aws_lambda_function" "hello_lambda" {
  function_name = "LINALambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lina.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  timeout = 10
  memory_size = 128
}

output "lambda_function_name" {
  value = aws_lambda_function.hello_lambda.function_name
  description = "Name of the Lambda function"
}

output "lambda_function_arn" {
  value = aws_lambda_function.hello_lambda.arn
  description = "ARN of the Lambda function"
}

output "lambda_execution_role_arn" {
  value = aws_iam_role.lambda_exec_role.arn
  description = "IAM Role ARN for Lambda Execution"
}
