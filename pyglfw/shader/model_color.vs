#version 330 core

layout (location = 0) in vec4 position;
layout (location = 1) in vec3 color;

out vec3 ourColor;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * position;
    // gl_Position = projection * view * position;
    ourColor = color;
}