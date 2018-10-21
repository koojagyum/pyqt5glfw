#version 330 core

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 ourColor;
in vec3 fragPos;
in vec3 fragNormal;
out vec4 color;

uniform vec3 viewPos;
uniform DirLight dirLight;
uniform PointLight pointLight;

vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir);
vec3 calcPointLight(PointLight light, vec3 normal, vec3 viewDir);

void main()
{
    // vec3 norm = normalize(fragNormal);
    vec3 norm = fragNormal;
    vec3 viewDir = normalize(viewPos - fragPos);

    // Phase 1: Directional lighting
    vec3 result = calcDirLight(dirLight, norm, viewDir);
    // Phase 2: Point lights
    result += calcPointLight(pointLight, norm, viewDir);

    color = vec4(result, 1.0);
}

vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);
    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // Specular shading
    // vec3 reflectDir = reflect(-lightDir, normal);
    // float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // Combine results
    // vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    // vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    // vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    // return (ambient + diffuse + specular);

    // temp
    vec3 diffuse = light.diffuse * diff * ourColor;
    return diffuse;
    // return ourColor;
    // return viewDir;
    // return normal;
}

vec3 calcPointLight(PointLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // Specular shading
    // vec3 reflectDir = reflect(-lightDir, normal);
    // float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // Attenuation
    float d = length(light.position - fragPos);
    float attenuation;
    if (light.constant == 0.0 && light.linear == 0.0 && light.quadratic == 0.0) {
        attenuation = 1.0;
    }
    else {
        attenuation = 1.0 / (light.constant + light.linear * d + light.quadratic * (d * d));
    }

    // Combine results
    // vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    // vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    // vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    // ambient *= attenuation;
    // diffuse *= attenuation;
    // specular *= attenuation;
    // return (ambient + diffuse + specular);

    vec3 diffuse = light.diffuse * diff * ourColor * attenuation;
    return diffuse;
    // return light.diffuse * diff * ourColor;
}
